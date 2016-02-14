"""
@author Thomas Churchman

Module to provide some utility functions.
"""

from hashlib import sha1
import random
import time
import ctypes
import appstate
import struct
from socket import inet_aton
from hash.hash import Hash

def chunks(str, chunkLength):
    """
    Split a string into chunks of length chunkLength.
    """
    if len(str) % chunkLength != 0:
        raise Exception('Expected str length to be a multiple of chunkLength')
        
    return (str[0+i:chunkLength+i] for i in range(0, len(str), chunkLength))
    
def randomBits(numBits):
    """
    Generate random bits
    """
    return random.getrandbits(numBits)
    
def getToken(node, timeDiff=0):
    """
    Procedurally generate a token for a node for get_peers and announce_peer.
    
    Tokens changes every 5 minutes.
    """
    t = int(time.time() / (60 * 5)) + int(timeDiff)
    ip = struct.unpack("<L", inet_aton(node.address()))[0]
    port = node.port()
    secret = appstate.AppState.tokenSecret
    
    return Hash(sha1(str(t + ip + port + secret).encode("utf-8")).digest())

def signedToUnsigned(i, bits=160):
    """
    'Cast' an integer from signed to unsigned
    """
    return i % (2**bits)

def isTokenValid(node, token):
    """
    Validate a given token for a given node.
    
    Tokens of up to 10 minutes old are accepted.
    """
    return token == getToken(node, 0) or token == getToken(node, -1)