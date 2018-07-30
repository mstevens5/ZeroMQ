#!/usr/bin/env python3

from crypto import *
import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: gen_key_pair.py private_key_file public_key_file")
        sys.exit()
    privFilename = sys.argv[1]
    pubFilename = sys.argv[2]
    privKey = gen_priv_key()
    pubKey = gen_pub_key(privKey)
    save_pem_priv_key(privKey, privFilename)
    save_pem_pub_key(pubKey, pubFilename)

