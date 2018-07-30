#!/usr/bin/env python3

# Source: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

# Taken from cryptography.io
def gen_priv_key():
    privateKey = rsa.generate_private_key(
        public_exponent = 65537,
        key_size = 2048,
        backend = default_backend()
    )
    return privateKey

# Taken from cryptography.io
def save_pem_priv_key(key, filename):
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format = serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm = serialization.NoEncryption()
    )
    with open(filename, 'wb') as fp:
        fp.write(pem)
    return pem

# Taken from cryptography.io
# reads from private key pem file and returns RSAPublicKey type
def load_pem_priv_key(filename):
    with open(filename, "rb") as keyFile:
        privKey = serialization.load_pem_private_key(
            keyFile.read(),
            password=None,
            backend = default_backend()
        )
    return privKey

# Taken from cryptography.io
def load_pem_pub_key(filename):
    with open(filename, "rb") as keyFile:
        pubKey = serialization.load_pem_public_key(
            keyFile.read(), 
            backend=default_backend()
        )
    return pubKey

# Taken from cryptography.io
def save_pem_pub_key(pubKey, filename):
    pem = pubKey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(filename, 'wb') as fp:
        fp.write(pem)
    return pem

# Taken from cryptography.io
def gen_pub_key(privKey):
    pubKey = privKey.public_key()
    return pubKey

# message is a bytes type
# privKey is RSAPrivateKey type. This can be obtained by calling 
# load_pem_priv_key()
# This function returns a digital signature as bytes type
def sign_message(message, privKey):
    signature = privKey.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length = padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

# Verify is the signature came from the message, using public key pubKey
# pubKey is RSAPublicKey type. This can be obtained by calling
# load_pem_pub_key()
# message is bytes type
def verify_message(signature, message, pubKey):
    try:
        pubKey.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except InvalidSignature as e:
        print("Invalid Signature verfication: %s" % e)
    else:
        print("Verified successfullly")

# encypt plaintext with pubKey usng RSA encryption
# plaintext: bytes type
# pubKey: RSAPublicKey type
# return: bytes type
def rsa_pub_key_encrypt(plaintext, pubKey):
    ciphertext = pubKey.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

# decypt ciphertext with privKey usng RSA encryption
# ciphertext: bytes type
# privKey: RSAPrivateKey type
# return: bytes type
def rsa_priv_key_decrypt(ciphertext, privKey):
    plaintext = privKey.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext




# AES Encryption ###############

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as pad

# all parameters should be bytes type
def aes_cbc_encrypt(key, iv, plaintext):
    padder = padding.PKCS7(128).padder()
    plaintext = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), 
        backend = default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(plaintext) + encryptor.finalize()

# all parameters should be bytes type
def aes_cbc_decrypt(key, iv, ciphertext):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), 
        backend = default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(plaintext) + unpadder.finalize()
    return plaintext
