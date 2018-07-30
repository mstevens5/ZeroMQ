#!/usr/bin/env python3

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.parser import BytesParser
from email.parser import Parser
#from common import *

import os
import sys
import configparser

from crypto import *

import pathlib
import hashlib
def md5(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()

def mkdir_p(dir):
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

def newFile(dir, name):
    mkdir_p(dir)
    return open(dir + '/' + name, 'w', encoding="utf-8")

def exists(file):
    return os.path.exists(file)

configFile = './config.ini'


import gzip
import shutil

# Compress contents  of 'plainFile' arg, and write to 'gzipFile'
def gzip_file_from_file(plainFile, gzipFile):
    with open(plainFile, 'rb') as f_in:
        with gzip.open(gzipFile, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

# Compress 'content' arg (bytes type) and write to 'gzipFile'
def gzip_file_from_string(content, gzipFile):
    with gzip.open(gzipFile, 'wb') as fd:
        fd.write(content)

# Compress 'content' (bytes type) and return as bytes type
def gzip_string_from_string(content):
    return gzip.compress(content)

def create_envelope(recipient, sequenceNumber, timeValidity, inputDir):
    outer = MIMEMultipart()
    outer['IntendedRecipient'] = recipient
    outer['SequenceNumber'] = sequenceNumber
    outer['TimeValidity'] = timeValidity
    outer['BundleState'] = 'Envelope'
    #outer.preamble = "\r\n\r\n"

    filesToRemove = []

    mkdir_p(inputDir)
    numFiles = 0
    for filename in os.listdir(doneDir):
        path = os.path.join(doneDir, filename)

        if not os.path.isfile(path):
            continue

        # Hardcoded mimetype, mimeguesser can be used to support multiple i
        # file types
        maintype = 'application'
        subtype = 'gzip'

        # Open data file to be included in bundle
        fp = open(path, 'rb')

        # MIMEBase is a general message type. The Content-Type header for this
        # message is set with the maintype and subtype arguments
        msg = MIMEBase(maintype, subtype)

        # Set payload with gzip-compressed file
        msg.set_payload(gzip_string_from_string(fp.read()))
        fp.close()
        
        filesToRemove.append(path)

        # Encode using Base64
        encoders.encode_base64(msg)

        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment', filename=filename)

        # Write to bundle
        outer.attach(msg)

        numFiles += 1

    if numFiles > 0:
        composed = outer.as_string()
    else:
        composed = ''
    return composed

    #for path in filesToRemove:
        #os.remove(path)

def add_signature(contents, signature):
    outer = MIMEMultipart()
    outer['BundleState'] = 'ServerFormat'
    
    maintype = 'text'
    subtype = 'plain'
    msg = MIMEBase(maintype, subtype)
    
    # Add headers. NOTE: Header values must NOT contain any spaces, CTRL, 
    # or colon characters. Doing so will result in a parser interpreting the
    # header as part of the body of the message (payload)
    msg['Type'] = 'Envelope'
    msg.add_header('Content-Disposition', 'inline')
    msg.set_payload(contents.encode('utf-8'))
    outer.attach(msg)

    msg = MIMEBase(maintype, subtype)
    msg['Type'] = 'Signature'
    msg.add_header('Content-Disposition', 'inline')
    
    msg.set_payload(signature)
    encoders.encode_base64(msg)
    outer.attach(msg)

    return outer.as_bytes()

# bundle is bytes type
def encrypt_bundle(key, iv, bundle, pubKey):
    keySig = sign_message(key, pubKey)
    ivSig = sign_messgae(iv, pubKey)
    encBundle = aes_cbc_encrypt(key, iv, bundle)
    outer = MIMMultipart()
    outer['BundleState'] = 'Encrypted_Bundle_Without_Signature']
    maintype = 'text'
    subtype = 'plain'

    msg = MIMEBase(maintype, subtype)

    msg['Type'] = 'Server_Format'
    msg.add_header['Content-Disposition', 'inline')
    msg.set_payload_base64(encBundle)
    encoders.encode(msg)
    outer.attach(msg)

    msg = MIMEBase(maintype, subtype)
    msg['Type'] = 'Signed_Encryption_Key'
    msg.add_header('Content-Disposition', 'inline')
    msg.set_payload(rsa_pub_key_encrypt(key, pubKey))
    encoders.encode_base64(msg)
    outer.attach(msg)

    msg = MIMEBase(maintype, subtype)
    msg['Type'] = 'Signed_Encryption_IV'
    msg.add_header('Content-Disposition', 'inline')
    msg.set_payload(rsa_pub_key_encrypt(iv, pubKey))
    encoders.encode_base64(msg)
    outer.attach(msg)

    return outer.as_string()

if __name__ == '__main__':

    '''
    privKey = load_pem_priv_key("./pkey1.pem")
    with open('./config.ini', 'rb') as messageFile:
        message = messageFile.read()

    print(message.decode('utf-8', 'strict'))
    signature = sign_message(message, privKey)
    print(type(signature))
    pubKey = load_pem_pub_key("./pubkey.pem")
    verify_message(signature, message, pubKey)
    sys.exit()

    '''
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
        privKeyFile = config['bundle_creator']['priv_key_file']
        serverPubKeyFile = config['bundle_creator']['server_pub_key_file']
        serverPrivKeyFile = config['bundle_creator']['server_priv_key_file']
    except KeyError as err:
        print('Missing key: {}'.format(err))
        exit(1)

    sequenceFile = open(sequenceFileName, 'r', encoding="utf-8")
    sequenceNumber = int(sequenceFile.read())
    sequenceFile.close()

    
    composed = create_envelope('Backend Server', str(sequenceNumber), sys.argv[1], 
        doneDir)

    if len(composed) <= 0:
        print("Error, no raw data files")
        sys.exit()
        
    sequenceFile = open(sequenceFileName, 'w', encoding="utf-8")
    sequenceFile.write('{}'.format(sequenceNumber + 1))
    sequenceFile.close()
    
    privKey = load_pem_priv_key(privKeyFile)

    signature = sign_message(composed.encode('utf-8'), privKey)

    composed = add_signature(composed, signature)
    
    serverPubKey = load_pem_pub_key(serverPubKeyFile)
    serverPrivKey = load_pem_priv_key(serverPrivKeyFile)
    

    key = os.urand(16)
    iv = os.urand(16)
    encrypt_bundle(key, iv, composed, serverPubKey)
    
    
    fp = newFile(bunDir, md5(composed))
    fp.write(composed)
    fp.close()
    

    # Read file and parse contents

    fp = open(bunDir + '/' + md5(composed), 'rb')
    #parser = Parser()
    parser = BytesParser()
    #msg = parser.parsestr(composed)
    msg = parser.parse(fp)
    fp.close()
    print(msg.as_string(), end='')
    


    #for path in filesToRemove:
        #os.remove(path)
