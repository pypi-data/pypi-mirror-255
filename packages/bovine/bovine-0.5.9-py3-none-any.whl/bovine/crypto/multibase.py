# SPDX-FileCopyrightText: 2024 helge
#
# SPDX-License-Identifier: MIT

from enum import Enum
from typing import Union

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, ec
from cryptography.hazmat.primitives.serialization import load_der_public_key
import based58


class MultiCodec(Enum):
    """The used Multicodec prefixes"""

    Ed25519Public = b"\xed\x01"
    EcP256Public = b"\x80$"
    EcP384Public = b"\x81\x24"
    RsaPublic = b"\x85$"

    Ed25519Private = b"\x80\x26"
    EcP256Private = b"\x86\x26"


def multibase_58btc_encode(data: bytes) -> str:
    """Encodes `data` in base 58 using the bitcoin alphabet
    and adds the prefix `z`"""
    return "z" + based58.b58encode(data).decode("utf-8")


def multibase_decode(data: str) -> bytes:
    """Decodes the string data using the multibase algorithm

    :param data: The string to decode
    :return: The bytes"""
    if data[0] == "z":
        return based58.b58decode(data[1:].encode("utf-8"))

    raise ValueError(f"{data} encoded in unknown format")


def encode_public_key_to_multibase(public_key) -> str:
    match public_key:
        case rsa.RSAPublicKey():
            public_bytes = MultiCodec.RsaPublic.value + public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            return multibase_58btc_encode(public_bytes)
        case ed25519.Ed25519PublicKey():
            return multibase_58btc_encode(
                MultiCodec.Ed25519Public.value
                + public_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw,
                )
            )
        case ec.EllipticCurvePublicKey():
            public_bytes = public_key.public_bytes(
                serialization.Encoding.X962,
                serialization.PublicFormat.CompressedPoint,
            )
            if isinstance(public_key.curve, ec.SECP256R1):
                return multibase_58btc_encode(
                    MultiCodec.EcP256Public.value + public_bytes
                )
            if isinstance(public_key.curve, ec.SECP384R1):
                return multibase_58btc_encode(
                    MultiCodec.EcP384Public.value + public_bytes
                )
    raise ValueError("Unsupported key type")


def decode_multibase_public_key(multibase_public_key):
    public_key = multibase_decode(multibase_public_key)

    match public_key[:2]:
        case MultiCodec.Ed25519Public.value:
            return ed25519.Ed25519PublicKey.from_public_bytes(public_key[2:])
        case MultiCodec.RsaPublic.value:
            return load_der_public_key(public_key[2:])
        case MultiCodec.EcP256Public.value:
            return ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256R1(), public_key[2:]
            )
        case MultiCodec.EcP384Public.value:
            return ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP384R1(), public_key[2:]
            )
    return None


def multibase_to_private_key(
    multibase: str,
) -> Union[ed25519.Ed25519PrivateKey, ec.EllipticCurvePrivateKey]:
    decoded = multibase_decode(multibase)
    if decoded[:2] == MultiCodec.Ed25519Private.value:
        return ed25519.Ed25519PrivateKey.from_private_bytes(decoded[2:])
    if decoded[:2] == MultiCodec.EcP256Private.value:
        return ec.derive_private_key(int.from_bytes(decoded[2:]), ec.SECP256R1())
    raise ValueError(f"Improper start for ed25519 private key. Got {str}")
