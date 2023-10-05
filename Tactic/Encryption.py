from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
import cryptography.hazmat.primitives.asymmetric as asymmetric
import os

class Encryption:
    def __init__(self):
        self.private_key, self.public_key = self.generate_rsa_keys()
        self.aes_key = None

    @staticmethod
    def generate_rsa_keys():
        private_key = asymmetric.rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def serialize_public_key(public_key):
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @staticmethod
    def deserialize_public_key(public_key_bytes):
        return serialization.load_pem_public_key(
            public_key_bytes,
            backend=default_backend()
        )

    @staticmethod
    def generate_aes_key():
        return os.urandom(32)

    def encrypt_with_public_key(self, public_key, message):
        return public_key.encrypt(
            message,
            asymmetric.padding.OAEP(
                mgf=asymmetric.padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def decrypt_with_private_key(self, ciphertext):
        return self.private_key.decrypt(
            ciphertext,
            asymmetric.padding.OAEP(
                mgf=asymmetric.padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
