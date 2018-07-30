#!/usr/bin/env python3

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

import sys
from crypto import *

padder = padding.PKCS7(128).padder()
str1 = "Hello world today is going to be a day. It might be great day on"
padded_str = padder.update(str1.encode('utf-8'))
print(padded_str)
padded_str += padder.finalize()
print(padded_str)
backend = default_backend()
key = os.urandom(16)
iv = os.urandom(16)
print(type(key))
cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend = backend)
encryptor = cipher.encryptor()
ct = encryptor.update(padded_str) + encryptor.finalize()
print(ct)
decipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend = backend)
decryptor = decipher.decryptor()
dct = decryptor.update(ct) + decryptor.finalize()
print(dct.decode('utf-8'))

key = os.urandom(16)
iv = os.urandom(16)
text = "Hello world today is going to be a day!"
if len(sys.argv) == 2:
    text = sys.argv[1]
ciph = aes_cbc_encrypt(key, iv, text.encode('utf-8'))
print(ciph)
plain = aes_cbc_decrypt(key, iv, ciph)
print(plain)


