# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

import pytest

from .types import CryptographicIdentifier


def test_verify_document():
    credential = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://w3id.org/security/data-integrity/v2",
        ],
        "id": "urn:uuid:86294362-4254-4f36-854f-3952fe42555d",
        "type": ["VerifiableCredential"],
        "issuer": "did:key:z6MktKwz7Ge1Yxzr4JHavN33wiwa8y81QdcMRLXQsrH9T53b",
        "issuanceDate": "2020-03-16T22:37:26.544Z",
        "credentialSubject": {
            "id": "did:key:z6MktKwz7Ge1Yxzr4JHavN33wiwa8y81QdcMRLXQsrH9T53b"
        },
        "proof": {
            "type": "DataIntegrityProof",
            "created": "2023-12-28T11:26:24Z",
            "verificationMethod": "did:key:z6MktKwz7Ge1Yxzr4JHavN33wiwa8y81QdcMRLXQsrH9T53b#z6MktKwz7Ge1Yxzr4JHavN33wiwa8y81QdcMRLXQsrH9T53b",
            "cryptosuite": "eddsa-rdfc-2022",
            "proofPurpose": "assertionMethod",
            "proofValue": "z59CRYvhTxnciJNtNAhp4fb5CbQvkMAZywYPrxDNu2d7CLn2kemf52BfnpA9hJJejzUv2zEmAA545ZBcf4aPg2BaM",
        },
    }
    did_key = "did:key:z6MktKwz7Ge1Yxzr4JHavN33wiwa8y81QdcMRLXQsrH9T53b"
    identifier = CryptographicIdentifier.from_did_key(did_key)

    assert identifier.verify_document(credential) == did_key


# Test data from https://www.w3.org/TR/vc-di-ecdsa/#representation-ecdsa-rdfc-2019-with-curve-p-256


def test_verify_document_w3c_recommendation_p256():
    credential = {
        "@context": [
            "https://www.w3.org/ns/credentials/v2",
            "https://www.w3.org/ns/credentials/examples/v2",
        ],
        "id": "urn:uuid:58172aac-d8ba-11ed-83dd-0b3aef56cc33",
        "type": ["VerifiableCredential", "AlumniCredential"],
        "name": "Alumni Credential",
        "description": "A minimum viable example of an Alumni Credential.",
        "issuer": "https://vc.example/issuers/5678",
        "validFrom": "2023-01-01T00:00:00Z",
        "credentialSubject": {
            "id": "did:example:abcdefgh",
            "alumniOf": "The School of Examples",
        },
        "proof": {
            "type": "DataIntegrityProof",
            "cryptosuite": "ecdsa-rdfc-2019",
            "created": "2023-02-24T23:36:38Z",
            "verificationMethod": "https://vc.example/issuers/5678#zDnaepBuvsQ8cpsWrVKw8fbpGpvPeNSjVPTWoq6cRqaYzBKVP",
            "proofPurpose": "assertionMethod",
            "proofValue": "z4KKHqaD4F7GHyLA6f3wK9Ehxtogv5jQRFpQBM4sXkSf7Bozd7bAf7dF6UkfM2aSCBMm24mPvaFXmzQmimzaEC3SL",
        },
    }
    controller = "https://vc.example/issuers/5678"

    identifier = CryptographicIdentifier.from_tuple(
        controller, "zDnaepBuvsQ8cpsWrVKw8fbpGpvPeNSjVPTWoq6cRqaYzBKVP"
    )
    assert identifier.verify_document(credential) == controller


# Test data from https://www.w3.org/TR/vc-di-ecdsa/#representation-ecdsa-rdfc-2019-with-curve-p-384


def test_verify_document_w3c_recommendation_p386():
    credential = {
        "@context": [
            "https://www.w3.org/ns/credentials/v2",
            "https://www.w3.org/ns/credentials/examples/v2",
        ],
        "id": "urn:uuid:58172aac-d8ba-11ed-83dd-0b3aef56cc33",
        "type": ["VerifiableCredential", "AlumniCredential"],
        "name": "Alumni Credential",
        "description": "A minimum viable example of an Alumni Credential.",
        "issuer": "https://vc.example/issuers/5678",
        "validFrom": "2023-01-01T00:00:00Z",
        "credentialSubject": {
            "id": "did:example:abcdefgh",
            "alumniOf": "The School of Examples",
        },
        "proof": {
            "type": "DataIntegrityProof",
            "cryptosuite": "ecdsa-rdfc-2019",
            "created": "2023-02-24T23:36:38Z",
            "verificationMethod": "https://vc.example/issuers/5678#z82LkuBieyGShVBhvtE2zoiD6Kma4tJGFtkAhxR5pfkp5QPw4LutoYWhvQCnGjdVn14kujQ",
            "proofPurpose": "assertionMethod",
            "proofValue": "zpuEu1cJ7Wpb453b4RiV3ex7SKGYm3fdAd4WUTVpR8Me3ZXkCCVUfd4M4TvHF9Wv1tRNWe5SkZhQTGYLUxdugFRGC2uyYRNTnimS6UMN6wkenTViRK1Mei7DooSBpumHHjYu",
        },
    }
    controller = "https://vc.example/issuers/5678"

    identifier = CryptographicIdentifier.from_tuple(
        controller,
        "z82LkuBieyGShVBhvtE2zoiD6Kma4tJGFtkAhxR5pfkp5QPw4LutoYWhvQCnGjdVn14kujQ",
    )
    assert identifier.verify_document(credential) == controller


# Test data from https://www.w3.org/TR/vc-di-ecdsa/#representation-ecdsa-jcs-2019-with-curve-p-384


def test_verify_document_w3c_recommendation_p386_jcs():
    credential = {
        "@context": [
            "https://www.w3.org/ns/credentials/v2",
            "https://www.w3.org/ns/credentials/examples/v2",
        ],
        "id": "urn:uuid:58172aac-d8ba-11ed-83dd-0b3aef56cc33",
        "type": ["VerifiableCredential", "AlumniCredential"],
        "name": "Alumni Credential",
        "description": "A minimum viable example of an Alumni Credential.",
        "issuer": "https://vc.example/issuers/5678",
        "validFrom": "2023-01-01T00:00:00Z",
        "credentialSubject": {
            "id": "did:example:abcdefgh",
            "alumniOf": "The School of Examples",
        },
        "proof": {
            "type": "DataIntegrityProof",
            "cryptosuite": "ecdsa-jcs-2019",
            "created": "2023-02-24T23:36:38Z",
            "verificationMethod": "https://vc.example/issuers/5678#z82LkuBieyGShVBhvtE2zoiD6Kma4tJGFtkAhxR5pfkp5QPw4LutoYWhvQCnGjdVn14kujQ",
            "proofPurpose": "assertionMethod",
            "proofValue": "zFYhRwKuucKxM7dnL69VpnwmU9UD2wc5HfFjXfxKH82pEybv18EfxaT8m53kyMfrDQneYnsLCZ35UE2KwZTkd4zN7vNHdVseyjW5apJJ9NkfpUiTGUayG2yaZvWu6Gd8EDYk",
        },
    }

    controller = "https://vc.example/issuers/5678"

    identifier = CryptographicIdentifier.from_tuple(
        controller,
        "z82LkuBieyGShVBhvtE2zoiD6Kma4tJGFtkAhxR5pfkp5QPw4LutoYWhvQCnGjdVn14kujQ",
    )
    assert identifier.verify_document(credential) == controller


# credential from https://github.com/w3c/vc-test-suite-implementations/pull/11#issuecomment-1874285663


def test_verify_document_from_digital_bazaar():
    credential = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            {
                "@protected": True,
                "DriverLicenseCredential": "urn:example:DriverLicenseCredential",
                "DriverLicense": {
                    "@id": "urn:example:DriverLicense",
                    "@context": {
                        "@protected": True,
                        "id": "@id",
                        "type": "@type",
                        "documentIdentifier": "urn:example:documentIdentifier",
                        "dateOfBirth": "urn:example:dateOfBirth",
                        "expirationDate": "urn:example:expiration",
                        "issuingAuthority": "urn:example:issuingAuthority",
                    },
                },
                "driverLicense": {"@id": "urn:example:driverLicense", "@type": "@id"},
            },
            "https://w3id.org/security/data-integrity/v2",
        ],
        "id": "urn:uuid:6a6a9bb2-090a-4ffa-8462-4a614ae4c269",
        "type": ["VerifiableCredential", "DriverLicenseCredential"],
        "credentialSubject": {
            "id": "urn:uuid:1a0e4ef5-091f-4060-842e-18e519ab9440",
            "driverLicense": {
                "type": "DriverLicense",
                "documentIdentifier": "T21387yc328c7y32h23f23",
                "dateOfBirth": "01-01-1990",
                "expirationDate": "01-01-2030",
                "issuingAuthority": "VA",
            },
        },
        "issuer": "did:key:zDnaeRZqxu4dSRPiLWwph8ghUy17tE9BWXTNqtpzTw2HjthdX",
        "issuanceDate": "2024-01-02T16:13:22Z",
        "proof": {
            "type": "DataIntegrityProof",
            "created": "2024-01-02T16:13:22Z",
            "verificationMethod": "did:key:zDnaeRZqxu4dSRPiLWwph8ghUy17tE9BWXTNqtpzTw2HjthdX#zDnaeRZqxu4dSRPiLWwph8ghUy17tE9BWXTNqtpzTw2HjthdX",
            "cryptosuite": "ecdsa-rdfc-2019",
            "proofPurpose": "assertionMethod",
            "proofValue": "z65xxPTTzV6w4Jtjiscbr5cX6QT5XJFZKC74hE6pzeboEGXknnVu8qT3JhBAJ12MdBWrVsEsuqWbh9Mb8StgF563N",
        },
    }
    did_key = "did:key:zDnaeRZqxu4dSRPiLWwph8ghUy17tE9BWXTNqtpzTw2HjthdX"
    identifier = CryptographicIdentifier.from_did_key(did_key)

    assert identifier.verify_document(credential) == did_key


# credential from https://github.com/w3c/vc-test-suite-implementations/pull/11#issuecomment-1874285663


@pytest.mark.skip
def test_verify_document_from_digital_bazaar_p386():
    credential = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            {
                "@protected": True,
                "DriverLicenseCredential": "urn:example:DriverLicenseCredential",
                "DriverLicense": {
                    "@id": "urn:example:DriverLicense",
                    "@context": {
                        "@protected": True,
                        "id": "@id",
                        "type": "@type",
                        "documentIdentifier": "urn:example:documentIdentifier",
                        "dateOfBirth": "urn:example:dateOfBirth",
                        "expirationDate": "urn:example:expiration",
                        "issuingAuthority": "urn:example:issuingAuthority",
                    },
                },
                "driverLicense": {"@id": "urn:example:driverLicense", "@type": "@id"},
            },
            "https://w3id.org/security/data-integrity/v2",
        ],
        "id": "urn:uuid:1e30cef5-6a61-4703-809f-9b7df5bde1a3",
        "type": ["VerifiableCredential", "DriverLicenseCredential"],
        "credentialSubject": {
            "id": "urn:uuid:1a0e4ef5-091f-4060-842e-18e519ab9440",
            "driverLicense": {
                "type": "DriverLicense",
                "documentIdentifier": "T21387yc328c7y32h23f23",
                "dateOfBirth": "01-01-1990",
                "expirationDate": "01-01-2030",
                "issuingAuthority": "VA",
            },
        },
        "issuer": "did:key:z82Lky21MA8mGLTpsgvGnikRjS12Ar8wik7L3BJi9xSvU89rZaKcNRrcddPHhNFTWdR84oB",
        "issuanceDate": "2024-01-03T15:15:20Z",
        "proof": {
            "type": "DataIntegrityProof",
            "created": "2024-01-03T15:15:20Z",
            "verificationMethod": "did:key:z82Lky21MA8mGLTpsgvGnikRjS12Ar8wik7L3BJi9xSvU89rZaKcNRrcddPHhNFTWdR84oB#z82Lky21MA8mGLTpsgvGnikRjS12Ar8wik7L3BJi9xSvU89rZaKcNRrcddPHhNFTWdR84oB",
            "cryptosuite": "ecdsa-rdfc-2019",
            "proofPurpose": "assertionMethod",
            "proofValue": "zrqP9MFHdZuRfF8jeFm57dQsqGpsv2JNHjCUy1Vrm7QJqwyesYkVv3ewn2SyH6MMgvVWzhNUziBUwZtwGW7CkA81GTMPYBb2ubKvMTXqhq2kwVwbC1oSEECevDHuhxdGqHaY",
        },
    }

    did_key = "did:key:z82Lky21MA8mGLTpsgvGnikRjS12Ar8wik7L3BJi9xSvU89rZaKcNRrcddPHhNFTWdR84oB"
    identifier = CryptographicIdentifier.from_did_key(did_key)

    assert identifier.verify_document(credential) == did_key


def test_verify_document_unsupported_cryptosuite():
    credential = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "id": "urn:uuid:09327695-56d3-4ef2-890c-d63b2b5e707f",
        "type": ["VerifiableCredential"],
        "credentialSubject": {
            "id": "did:key:z6MktKwz7Ge1Yxzr4JHavN33wiwa8y81QdcMRLXQsrH9T53b"
        },
        "issuer": "did:key:z6MkgND5U5Kedizov5nxeh2ZCVUTDRSmAfbNqPhzCq8b72Ra",
        "issuanceDate": "2020-03-16T22:37:26.544Z",
        "proof": {
            "@context": ["https://w3id.org/security/data-integrity/v1"],
            "type": "DataIntegrityProof",
            "proofPurpose": "assertionMethod",
            "proofValue": "z4ncyz44KMkma4Z4h3iVRx6W2tB7xVbMNGk8gc9BRtqNWWsixNazdshm1aZADEH3vNJxd9RMKBTMqhSCcSEH6tn8V",
            "verificationMethod": "did:key:z6MkgND5U5Kedizov5nxeh2ZCVUTDRSmAfbNqPhzCq8b72Ra#z6MkgND5U5Kedizov5nxeh2ZCVUTDRSmAfbNqPhzCq8b72Ra",
            "created": "2024-02-05T10:21:42.315Z",
            "cryptosuite": "eddsa-2022",
        },
    }

    did_key = "did:key:z6MkgND5U5Kedizov5nxeh2ZCVUTDRSmAfbNqPhzCq8b72Ra"
    identifier = CryptographicIdentifier.from_did_key(did_key)

    with pytest.raises(ValueError) as info:
        identifier.verify_document(credential)

    assert str(info.value) == "Unknown cryptosuite 'eddsa-2022'"
