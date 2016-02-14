import utils

class Hash:
    """
    Class to encapsulate SHA1 hash digests (i.e., 160-bit IDs).
    """
    def __init__(self, hash):
        #self.hash = str(hash)
        self.hash = hash

        if len(self.hash) != 20:
            raise ValueError("Hash is not 20 bytes")
         
        self.int = int.from_bytes(self.hash, byteorder='big', signed=False)
        
    def distance(self, otherHash):
        """
        Calculate distance between this hash and another hash
        by bitwise XORing the byte representations and 
        interpreting the output as an unsigned integer.
        """
        return utils.signedToUnsigned(int(self) ^ int(otherHash))
        
    def __int__(self):
        return self.int
        
    def __bytes__(self):
        return self.hash
        
    def __repr__(self):
        return "Hash(hash=%r)" % (self.hash)
        
    def __eq__(self, other):
        return bytes(self) == bytes(other)