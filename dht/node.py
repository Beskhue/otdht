"""
@author Thomas Churchman
"""

class Node:
    """
    Class to represent a node in the DHT network.
    """
    def __init__(self, hash, addressPort, bucket=None):
        (address, port) = addressPort
        
        self.hash = hash
        self.host = (address, port)
        self.bucket = bucket
        
    def address(self):
        (address, port) = self.host
        return address
        
    def port(self):
        (address, port) = self.host
        return port
        
    def distanceToNode(self, otherNode):
        return self.hash.distance(otherNode.hash)

    def distanceToHash(self, hash):
        return self.hash.distance(hash)

    def __bytes__(self):
        return bytes(self.hash)

    def __int__(self):
        return int(self.hash)
        
    def __repr__(self):
        (address, port) = self.host
        return "Node(hash=%r,(address=%r,port=%r),bucket=%r)" % (self.hash, address, port, self.bucket)