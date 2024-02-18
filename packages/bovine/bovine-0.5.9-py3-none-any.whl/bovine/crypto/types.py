# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

import base64
import logging

from dataclasses import dataclass
from cryptography.exceptions import InvalidSignature

from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, padding, ec, utils
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    load_pem_private_key,
)
from typing import Union, Tuple

import bovine.jsonld
import bovine.utils
from bovine.utils import pydantic_to_json
from bovine.models import DataIntegrityProof, Multikey
from .helper import (
    split_according_to_fep8b32,
    jcs_sha256,
    jcs_sha384,
    rdfc_sha256,
    rdfc_sha384,
    integrity_proof_to_pure_proof_dict,
    ensure_data_integrity_context,
    curve_to_hashing_algorithm_and_half_key_length,
)

from .multibase import (
    multibase_58btc_encode,
    decode_multibase_public_key,
    encode_public_key_to_multibase,
    multibase_to_private_key,
)


logger = logging.getLogger(__name__)


@dataclass
class CryptographicSecret:
    """Represents a cryptographic secret. Such a secret is composed
    of the private key and the URI that resolves to the material, one
    can construct the appropriate cryptographic identifier from.

    :param key_id: The URI, where the corresponding public key and controller
        can be retrieved
    :param private_key: The signing material
    """

    key_id: str
    private_key: Union[ed25519.Ed25519PrivateKey, rsa.RSAPrivateKey]

    def sign(self, message: str | bytes):
        """Signs the message.

        Currently only implemented for RSA: Uses PKCS1v15 padding and SHA256
        hashes. Returns the signature as base64 encoded.

        **Warning**: Interface might change, to enable specifying encoding
        of the signature.

        :param message: The message to sign as UTF-8 encoded string."""

        if isinstance(message, str):
            message = message.encode("utf-8")

        if isinstance(self.private_key, rsa.RSAPrivateKey):
            return base64.standard_b64encode(
                self.private_key.sign(
                    message,
                    padding.PKCS1v15(),
                    hashes.SHA256(),
                )
            ).decode("utf-8")
        if isinstance(self.private_key, ed25519.Ed25519PrivateKey):
            return multibase_58btc_encode(self.private_key.sign(message))
        if isinstance(self.private_key, ec.EllipticCurvePrivateKey):
            algorithm, length = curve_to_hashing_algorithm_and_half_key_length(
                self.private_key.curve
            )
            signature_dss = self.private_key.sign(message, algorithm)
            r, s = utils.decode_dss_signature(signature_dss)
            signature = r.to_bytes(length) + s.to_bytes(length)
            return multibase_58btc_encode(signature)

        raise ValueError("Unknown key type in private key")

    def sign_document(
        self,
        document: dict,
        use_rdfc: bool = False,
        proof_purpose="assertionMethod",
    ) -> dict:
        """Signs the current document according to the procedure
        outlined in [FEP-8b32](https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md). We support signing with
        [eddsa-jcs-2022 / eddsa-rdfc-2022](https://www.w3.org/TR/vc-di-eddsa/)
        and [ecdsa-jcs-2019 / eddsa-edfc-2019](https://www.w3.org/TR/vc-di-ecdsa/).
        The cryptosuite is chosen depending on the type of signing material
        and the `use_rdfc` parameter

        :param document: The document to sign
        :param use_rdfc: Set to `True` to use `eddsa-rdfc-2022` or `ecdsa-rdfc-2019`
        :param proof_purpose: Purpose of the proof
        """

        match [self.private_key, use_rdfc]:
            case [ed25519.Ed25519PrivateKey(), True]:
                cryptosuite = "eddsa-rdfc-2022"
                to_hash = rdfc_sha256
            case [ed25519.Ed25519PrivateKey(), False]:
                cryptosuite = "eddsa-jcs-2022"
                to_hash = jcs_sha256
            case [ec.EllipticCurvePrivateKey(), True]:
                cryptosuite = "ecdsa-rdfc-2019"
                if isinstance(self.private_key.curve, ec.SECP256R1):
                    to_hash = rdfc_sha256
                else:
                    to_hash = rdfc_sha384
            case [ec.EllipticCurvePrivateKey(), False]:
                cryptosuite = "ecdsa-jcs-2019"
                if isinstance(self.private_key.curve, ec.SECP256R1):
                    to_hash = jcs_sha256
                else:
                    to_hash = jcs_sha384
            case _:
                raise ValueError("Unsupported Key Format for signing documents")

        document_to_sign = ensure_data_integrity_context(document)

        created = bovine.utils.now_isoformat()
        proof = DataIntegrityProof(
            created=created,
            cryptosuite=cryptosuite,
            proofPurpose=proof_purpose,
            type="DataIntegrityProof",
            verificationMethod=self.key_id,
        )
        digest = to_hash(
            pydantic_to_json(proof),
            context=document_to_sign["@context"],
        ) + to_hash(document_to_sign, context=document_to_sign["@context"])
        proof.proofValue = self.sign(digest)

        return {
            **document_to_sign,
            "proof": pydantic_to_json(proof),
        }

    @classmethod
    def from_pem(cls, key_id: str, pem: str):
        """Creates a CryptographicSecret from a PEM encoded private key"""
        return cls(key_id, load_pem_private_key(pem.encode("utf-8"), password=None))

    @classmethod
    def from_multibase(cls, key_id: str, multibase: str):
        """Creates a CryptographicSecret from multibase encoded
        Ed25519 private key and key_id"""
        return cls(key_id, multibase_to_private_key(multibase))


@dataclass
class CryptographicIdentifier:
    """Represents a cryptographic identifier. The usage is: If an object is
    signed by `public_key`, then it is authored by `controller`. In order
    to discover which `CryptographicIdentifier` to use, one resolves another
    identifier `key_id`, which yields either a Multikey or a publicKey object, which
    can then be resolved into a CryptographicIdentifier.

    One should never need to directly access the properties of this class, instead
    verify returns the controller, if and only if the signature is valid.

    :param controller: The URI of the actor that controls the public key
    :param public_key: Public key used to verify signatures
    """

    controller: str
    public_key: Union[
        ed25519.Ed25519PublicKey, rsa.RSAPublicKey, ec.EllipticCurvePublicKey
    ]

    def verify(self, message: str | bytes, signature: str | bytes) -> str | None:
        """Verifies that `signature` is a correct signature for the given message.

        **Warning**: Interface might change, to enable specifying encoding
        of the signature.

        :param message: The message string.
        :param signature: The signature

        :return: If the signature is valid the corresponding controller,
            otherwise null.
        """
        # Doing the encoding here is probably wrong ...
        # All these things are awkward

        if isinstance(signature, str):
            signature = base64.standard_b64decode(signature)

        if isinstance(message, str):
            message = message.encode("utf-8")

        if isinstance(self.public_key, rsa.RSAPublicKey):
            try:
                self.public_key.verify(
                    signature,
                    message,
                    padding.PKCS1v15(),
                    hashes.SHA256(),
                )
                return self.controller
            except InvalidSignature:
                return None

        if isinstance(self.public_key, ed25519.Ed25519PublicKey):
            try:
                self.public_key.verify(signature, message)
                return self.controller
            except InvalidSignature:
                return None

        if isinstance(self.public_key, ec.EllipticCurvePublicKey):
            try:
                algorithm, length = curve_to_hashing_algorithm_and_half_key_length(
                    self.public_key.curve
                )

                r = int.from_bytes(signature[:length])
                s = int.from_bytes(signature[length:])

                logger.debug("R %d", r)
                logger.debug("S %d", s)

                signature_dss = utils.encode_dss_signature(r, s)

                logger.debug("Signature DSS length %d", len(signature_dss))

                self.public_key.verify(signature_dss, message, algorithm)
                return self.controller
            except InvalidSignature:
                return None

        raise ValueError("Unknown key type in public_key")

    def verify_document(self, document: dict):
        """Verifies that document has a valid signature according to FEP-8b32.
        We note that in order to verify a document signed using FEP-8b32, one
        will already need to parse it sufficiently to extract the controller,
        so the CryptographicIdentifier can be created.

        __Beware__: Verification with P-386 keys might be broken.

        :param document: The document to verify"""
        pure_doc, proof_doc, signature = split_according_to_fep8b32(document)
        pure_proof = integrity_proof_to_pure_proof_dict(proof_doc)

        match proof_doc.cryptosuite:
            case "eddsa-jcs-2022" | "ecdsa-jcs-2019":
                to_hash = jcs_sha256
                if isinstance(
                    self.public_key, ec.EllipticCurvePublicKey
                ) and isinstance(self.public_key.curve, ec.SECP384R1):
                    to_hash = jcs_sha384
            case "eddsa-rdfc-2022" | "ecdsa-rdfc-2019":
                to_hash = rdfc_sha256
                if isinstance(
                    self.public_key, ec.EllipticCurvePublicKey
                ) and isinstance(self.public_key.curve, ec.SECP384R1):
                    to_hash = rdfc_sha384
                    logger.info("USING rdfc_sha384")
            case _:
                logger.warning("Got the unknown cryptosuite %s", proof_doc.cryptosuite)
                raise ValueError(f"Unknown cryptosuite '{proof_doc.cryptosuite}'")

        digest_one = to_hash(pure_proof, context=pure_doc["@context"])
        digest_two = to_hash(pure_doc, context=pure_doc["@context"])
        logger.debug("Digest Proof %s", digest_one.hex())
        logger.debug("Digest Document %s %d", digest_two.hex(), len(digest_two))
        digest = digest_one + digest_two

        return self.verify(digest, signature)

    def as_tuple(self) -> Tuple[str, str]:
        """Transforms the CryptographicIdentifier into a tuple

        :return: controller, multibase/multicodec encoded public key"""
        public_key = encode_public_key_to_multibase(self.public_key)

        return (self.controller, public_key)

    @classmethod
    def from_pem(cls, public_key: str, owner: str):
        """Creates a CryptographicIdentifier from a pem encoded public key and the controller"""
        if public_key is None:
            return None
        return cls(
            controller=owner, public_key=load_pem_public_key(public_key.encode("utf-8"))
        )

    @classmethod
    def from_multikey(cls, multikey: dict):
        """Creates a CryptographicIdentifier from a Multikey, see

        * [FEP-521a: Representing actor's public keys](https://codeberg.org/fediverse/fep/src/branch/main/fep/521a/fep-521a.md)

        Example:

        ```json
        {
            "id": "https://server.example/users/alice#ed25519-key",
            "type": "Multikey",
            "controller": "https://server.example/users/alice",
            "publicKeyMultibase": "z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2"
        }
        ```
        """
        parsed = Multikey.model_validate(multikey)
        return cls.from_tuple(parsed.controller, parsed.publicKeyMultibase)

    @classmethod
    def from_tuple(cls, controller: str, multibase_public_key: str):
        """Creates a CryptographicIdentifier from a tuple

        :param controller: The controller URI
        :param multibase_public_key: The public key encoded using multibase/multicodex
        """
        public_key = decode_multibase_public_key(multibase_public_key)
        if public_key:
            return cls(
                controller=controller,
                public_key=public_key,
            )
        raise ValueError("Unsupported public key format")

    @classmethod
    def from_did_key(cls, did_key: str):
        """Creates a cryptographic identifier from a did:key
        The controller is then the did:key and the public key
        the encoded public key. See [The did:key Method](https://w3c-ccg.github.io/did-method-key/) for details. Currently supported: Ed25519, RSA, P-256, and P-384 keys.

        :param did_key: The did key, e.g. "did:key:z6MkekwC6R9bj9ErToB7AiZJfyCSDhaZe1UxhDbCqJrhqpS5"
        """

        if did_key.startswith("did:key:"):
            return cls.from_tuple(did_key, did_key[8:])

        raise ValueError("Invalid did key format")

    @classmethod
    def from_public_key(cls, data: dict):
        """Creates a Cryptographic identifier from a publicKey object, example:

        ```json
        {
            "id": "https://com.example/issuer/123#main-key",
            "owner": "https://com.example/issuer/123",
            "publicKeyPem": "-----BEGIN PUBLIC KEY-----\\n...\\n-----END PUBLIC KEY-----"
        }
        ```
        """
        controller = data.get("owner")
        public_key = data.get("publicKeyPem")

        if isinstance(public_key, dict):
            public_key = public_key.get("@value")

        if controller is None or public_key is None:
            raise ValueError(
                "Expected parameters owner and publicKeyPem to be present when parsing publicKey"
            )

        return cls(
            controller=controller,
            public_key=load_pem_public_key(public_key.encode("utf-8")),
        )
