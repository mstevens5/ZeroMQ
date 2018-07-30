
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
