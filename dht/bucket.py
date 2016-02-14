"""
@author Thomas Churchman

Module that provides node bucket functionality.
"""

import appstate

class Bucket:
    """
    Class to represent a bucket for use in the routing table.
    """
    def __init__(self, low, high, refreshed, nodes=[]):
        self.low = low # inclusive
        self.high = high # inclusive
        self.refreshed = refreshed
        self.nodes = nodes
        
    def inRange(self, node):
        """
        Check if the given node (ID) falls in this bucket's ID space.
        """
        return self.low <= node and node <= self.high
        
    def addNode(self, node):
        """
        Attempt to add a node to the bucket.
        """
        if not inRange(node):
            return False
        
        if len(self.nodes) >= appstate.AppState.maxBucketSize:
            return False

        if node in self.nodes:
            return False
           
        self.nodes.append(node)
        node.bucket = self
        
    def __repr__(self):
        return "Bucket(low=%r,high=%r,refreshed=%r,nodes=%r)" % (self.low, self.high, self.refreshed, self.nodes)