"""
@author Thomas Churchman

Module that provides routing table functionality.
"""

import dht.node
import dht.bucket
import hash.hash
import config

class RoutingTable:  
    """
    Class to represent a routing table.
    """
    
    def __init__(self, buckets: [dht.bucket.Bucket] = None):
        if buckets == None:
            self.buckets = []
        else:
            self.buckets = buckets
            
    def refresh(self):
        """
        Refresh the routing table
        """
        pass

    def addNode(self, node: dht.node.Node):
        """
        Attempt to add the given node to the routing table.
        """
        
        bucket = self._findBucket(node)
        if bucket == None:
            raise Exception("Found no bucket for given id")
        
        if not node in bucket:
            # We do not have this node on our routing table yet;
            # attempt to add it.
            if len(bucket) < MAX_NODES_PER_BUCKET:
                bucket.append(node)
            else:
                if bucket.inRange(myID):
                    # Our own node's ID is in the appropriate bucket's range,
                    # split the bucket and recursively attempt to add the node.
                    self._splitBucket(bucket)
                    self.addNode(node)
                else:
                    # TODO: handle this
                    pass
        
    def _findBucket(self, node):
        """
        Find the appropriate bucket for the given node
        """
        for bucket in buckets:
            if bucket.inRange(node):
                return bucket
            #if bucket.low <= node and node <= bucket.high:
            #    return bucket
        return None
        
    def findNode(self, target: hash.hash.Hash):
        """
        Find a node with the given ID in the routing table.
        """
        for bucket in self.buckets:
            if bucket.inRange(nodeID):
                for node in bucket:
                    if node.hash == target:
                        return node
                        
                return None
        return None
        
    def findClosestNodes(self, target: hash.hash.Hash):
        """
        Find the K nodes in the routing table closest to the given target ID.
        """
        # TODO: make more efficient
        # See: http://stackoverflow.com/questions/30654398/implementing-find-node-on-torrent-kademlia-routing-table
        
        nodes = []
        
        for bucket in self.buckets:
            nodes = nodes + bucket.nodes

        nodes.sort(key=lambda x: nodes.distanceToHash(targetHash))

        return nodes[:config.K]
        
    def _splitBucket(self, bucket):
        """
        Remove the given bucket from the routing table,
        split the bucket in two buckets each spanning halve
        the original bucket's ID space, redistribute the
        nodes to the appropriate buckets and add the buckets 
        to the routing table.
        """
        idx = self.buckets.index(bucket)
        self.buckets.pop(idx)
        middle = int(bucket.low + (bucket.high - bucket.low)/2)
        
        bucketLow = Bucket(bucket.low, middle, bucket.refreshed)
        bucketHigh = Bucket(middle+1, bucket.high, refreshed.refreshed)
        
        self.buckets.append(bucketLow)
        self.buckets.append(bucketHigh)
        
        for bucket in bucket.nodes:
            if bucketLow.inRange(bucket):
                bucketLow.addNode(bucket)
            else:
                bucketHigh.addNode(bucket)
        
        return (bucketLow, bucketHigh)
            
    def __repr__(self):
        return "RoutingTable(buckets=%r)" % (self.buckets)