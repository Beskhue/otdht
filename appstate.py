"""
@author Thomas Churchman

Module that provides the application state functionality.
"""

from hashlib import sha1

import config
import utils
from dht.routing import RoutingTable
from dht.node import Node
import dht.peerstorage
from hash.hash import Hash

class AppState:
    """
    Class to hold the global application state.
    """
    def prepare():
        """
        Prepare the application state.
        """
        thisNodeIP = config.NODE_IP
        thisNodePort = config.NODE_PORT
        thisNodeHash = Hash(sha1(config.NODE_ID_NAME).digest())
        AppState.thisNode = Node(thisNodeHash, (thisNodeIP, thisNodePort))
    
        AppState.heartbeat = config.HEARTBEAT

        AppState.tokenSecret = utils.randomBits(160)
    
        AppState.maxPeersPerTorrent = config.MAX_PEERS_PER_TORRENT
    
        AppState.k = config.K
        AppState.maxNodesPerPucket = config.MAX_NODES_PER_BUCKET
    
        AppState.routingTable = RoutingTable()
    
        if config.PEER_STORAGE == 'file':
            AppState.peerStorage = dht.peerstorage.FilePeerStorage(config.PEER_STORAGE_DIR)
        elif config.PEER_STORAGE == 'mysql':
            AppState.peerStorage = dht.peerstorage.MySQLPeerStorage()
    
        # {transactionID: {(RPCQuery, Node, timestamp)}}
        AppState.outstandingQueries = {}
    
