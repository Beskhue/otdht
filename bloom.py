"""
@author Thomas Churchman

Module implementing a bloom filter.
"""

import hashlib
import math
import ipaddress
from struct import pack

class BloomFilter:
    """
    Class representing a bloom filter.
    """
    K = 2
    M = 256 * 8
    def __init__(self):
        self.bloom = [0] * (self.M/8)
        
    def insertIP(self, ip):
        """
        Insert an IP into the bloom filter.
        """
        # IP to bytes
        bytes = ipaddress.ip_address(unicode(ip)).packed
        
        # Calculate SHA1 hash
        hash = hashlib.sha1(bytes).digest()
                
        # Convert characters to integers
        hash = map(ord, hash)
        
        index1 = hash[0] | (hash[1] << 8)
        index2 = hash[2] | (hash[3] << 8)
        
        # Truncate index to m (11 bits required)
        index1 %= self.M
        index2 %= self.M
        
        # Set bits at index1 and index2
        self.bloom[index1 / 8] |= 0x01 << (index1 % 8)
        self.bloom[index2 / 8] |= 0x01 << (index2 % 8)
        
    def _countZeroBits(self):
        """
        Count the number of zero bits in the bloom filter.
        """
        # Convert bloom filter to bytes
        bytes = map("{0:08b}".format, self.bloom)
        
        # Count number of zero-bits
        bytes = map(lambda byte: sum(bit == '0' for bit in byte), bytes)
        
        # Return sum of number of zero-bits
        return sum(bytes)
        
    def estimate(self):
        """
        Estimate the number of items in the bloom filter.
        """
        c = float(min(self.M-1, self._countZeroBits()))
        return math.log(c / self.M) / (self.K * math.log(1 - 1. / self.M))