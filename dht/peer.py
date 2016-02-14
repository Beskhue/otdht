"""
@author Thomas Churchman
"""

class Peer:
    """
    Class to represent a peer.
    """
    def __init__(self, addressPort, seeder=False):
        (address, port) = addressPort

        self.host = (address, port)
        self.seeder = seeder
        
    def address(self):
        (address, port) = self.host
        return address
    
    def port(self):
        (address, port) = self.host
        return port
    
    def __repr__(self):
        (address, port) = self.host
        return "Node((address=%r,port=%r),seeder=%r)" % (address, port, self.seeder)
        
    def __eq__(self, other):
        return (
            self.address() == other.address()
            and
            self.port() == other.port()
            and 
            self.seeder == other.seeder
        )
            