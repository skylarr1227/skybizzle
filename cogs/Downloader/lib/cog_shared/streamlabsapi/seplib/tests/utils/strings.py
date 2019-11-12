import binascii
import os


def random_string(bits: int = 16):
    return binascii.hexlify(os.urandom(bits)).decode("UTF-8")
