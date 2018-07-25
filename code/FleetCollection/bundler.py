#!/usr/bin/env python3

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from common import *

import configparser
import os
import sys

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Taken from cryptography.io
def gen_priv_key():
    private_key = rsa.generate_private_key(
        public_exponent = 65537,
        key_size = 2048,
        backend = default_backend()
    )
    return private_key

# Taken from cryptography.io
def save_pem_key(key, filename):
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format = serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm = serialization.NoEncryption()
    )
    with open(filename, 'wb') as fp:
        fp.write(pem)
    return pem

def load_pem_key(filename):
    with open(filename, "rb") as key_file:
        priv_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend = default_backend()
        )
    return priv_key

if __name__ == '__main__':
    priv_key = gen_priv_key()
    print(priv_key)
    save_pem_key(priv_key, "./pkey.pem")
    print(load_pem_key("./pkey.pem"))
    sys.exit()
    if len(sys.argv) < 2:
        print('Missing time validity argument')
        exit(1)

    sequenceFileName = 'sequence'
    if not exists(sequenceFileName):
        print('Missing file: {}'.format(sequenceFileName))
        exit(1)

    if not exists(configFile):
        print('Missing file: {}'.format(configFile))
        exit(1)

    config = configparser.ConfigParser()
    config.read(configFile)
    try:
        doneDir = config['general']['done_dir']
        bunDir = config['bundler']['output_dir']
        identifier = config['bundler']['identifier']
    except KeyError as err:
        print('Missing key: {}'.format(err))
        exit(1)

    sequenceFile = open(sequenceFileName, 'r', encoding="utf-8")
    sequenceNumber = int(sequenceFile.read())
    sequenceFile.close()

    # Header
    outer = MIMEMultipart()
    outer['Creator'] = identifier
    outer['CreationDate'] = '{:.3f}'.format(now())
    outer['SequenceNumber'] = '{}'.format(sequenceNumber)
    outer['TimeValidity'] = sys.argv[1]
    outer.preamble = "\r\n\r\n"

    inner = MIMEMultipart()
    inner.preamble = "\r\n\r\n"

    filesToRemove = []

    mkdir_p(doneDir)
    for filename in os.listdir(doneDir):
        path = os.path.join(doneDir, filename)

        if not os.path.isfile(path):
            continue

        # Hardcoded mimetype, mimeguesser can be used to support multiple file types
        maintype = 'application'
        subtype = 'gzip'

        # Read file and setup to be written to bundle
        fp = open(path, 'rb')
        msg = MIMEBase(maintype, subtype)
        msg.set_payload(fp.read())
        fp.close()
        filesToRemove.append(path)

        # Encode using Base64
        encoders.encode_base64(msg)

        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment', filename=filename)

        # Write to bundle
        inner.attach(msg)

    innerComposed = inner.as_string()

    # TODO: Encrypt
    encryptedInner = innerComposed

    # Attach the encrypted inner to outer
    maintype = 'application'
    subtype = 'gzip'
    msg = MIMEBase(maintype, subtype)
    msg.set_payload(encryptedInner)
    encoders.encode_base64(msg)
    msg.add_header('Content-Disposition', 'attachment', filename='encrypted')
    outer.attach(msg)

    composed = outer.as_string()
    fp = newFile(bunDir, md5(composed))
    fp.write(composed)
    fp.close()

    sequenceFile = open(sequenceFileName, 'w', encoding="utf-8")
    sequenceFile.write('{}'.format(sequenceNumber + 1))
    sequenceFile.close()

    for path in filesToRemove:
        os.remove(path)
