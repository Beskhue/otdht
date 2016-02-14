"""
@author Thomas Churchman

Module that provides methods for encoding and decoding 
KRCP messages.
"""

import functools
import struct
from socket import inet_aton
from socket import inet_ntoa

import bencodepy

import utils
from appstate import AppState
from dht.node import Node
from dht.peer import Peer
from hash.hash import Hash

def decode(data, addressPort):
    """
    Decode a datagram into a KRPC message.
    """
    msg = bencodepy.decode(data)
    (address, port) = addressPort

    type = msg[b'y']
    
    if type == b'q':
        krpc = _decodeQuery(msg, (address, port))
    elif type == b'r':
        krpc = _decodeResponse(msg, (address, port))
    elif type == b'e':
        krpc = _decodeError(msg, (address, port))
    else:
        raise Exception('Invalid RPC query type')
        
    return krpc
        
        
def _decodeQuery(rawRPC, addressPort):
    """
    Decode a KRPC query into a KRPC query object.
    """
    rpc = KRPCQuery()
    rpc.type = rawRPC[b'q']
    rpc.transactionID = rawRPC[b't']
    rpc.toNode = AppState.thisNode
    
    (address, port) = addressPort

    fromID = Hash(rawRPC[b'a'][b'id'])
    node = AppState.routingTable.findNode(fromID)
    if node == None:
        node = Node(fromID, (address, port))
    rpc.fromNode = node
    
    if rpc.type == b'ping':
        # Decode ping query
    
        pass
    elif rpc.type == b'find_node':
        # Decode find_node query
        
        rpc.targetID = Hash(rawRPC[b'a'][b'target'])
    elif rpc.type == b'get_peers':
        # Decode get_peers query
        
        rpc.targetID = Hash(rawRPC[b'a'][b'info_hash'])
        
        # Decode optional argument 'noseed'
        if 'noseed' in rawRPC[b'a'] and rawRPC[b'a'][b'noseed'] == 1:
            rpc.noSeeders = True
            
        # Decode optional argument 'scrape'
        if 'scrape' in rawRPC[b'a'] and rawRPC[b'a'][b'scrape'] == 1:
            rpc.scrape = True    
    elif rpc.type == b'announce_peer':
        # Decode announce_peer query
        rpc.targetID = Hash(rawRPC[b'a'][b'info_hash'])
        
        # Decode optional argument 'implied_port'
        if 'implied_port' in rawRPC[b'a'] and rawRPC[b'a'][b'implied_port'] == 1:
            peerPort = port
            rpc.impliedPort = True
        else:
            peerPort = int(rawRPC[b'a'][b'port'])
        
        # Decode optional argument 'seed'
        if 'seed' in rawRPC[b'a'] and rawRPC[b'a'][b'seed'] == 1:
            seeder = True
        else:
            seeder = False
            
        rpc.peer = Peer((address, peerPort), seeder)
        rpc.token = Hash(rawRPC[b'a'][b'token'])
                
    return rpc
    
def _decodeResponse(rawRPC, addressPort):
    """
    Decode a KRPC response into a KRPC response object.
    """
    rpc = KRPCResponse()
    rpc.transactionID = rawRPC[b't']
    rpc.toNode = AppState.thisNode
    
    (address, port) = addressPort

    try:
        (originalQuery, toNode, timestamp) = AppState.outstandingQueries[rpc.transactionID]
    except:
        raise Exception('No matching outstanding query transaction ID could be found.')
    
    rpc.responseTo = originalQuery
    
    if toNode.address != address or toNode.port != port:
        raise Exception('Matching query was sent to a different address or port than this response originated from.')
    
    
    rpc.type = originalQuery.type
    
    fromID = Hash(rawRPC[b'r'][b'id'])
    node = AppState.routingTable.findNode(fromID)
    if node == None:
        node = Node(fromID, (address, port))
    rpc.fromNode = node
    
    if rpc.type == b'ping':
        pass
    elif rpc.type == b'find_node':
        rpc.nodes = _decodeNodesInfo(rawRPC[b'r'][b'nodes'])
    elif rpc.type == b'get_peers':
        rpc.token = Hash(rawRPC[b'r'][b'token'])
        if b'nodes' in rawRPC[b'r']:
            rpc.nodes = _decodeNodesInfo(rawRPC[b'r'][b'nodes'])
        elif b'values' in rawRPC[b'r']:
            rpc.peers = _decodePeers(rawRPC[b'r'][b'values'])
        else:
            raise Exception('Expected either nodes or peers in get_peers response')
    elif rpc.type == b'announce_peer':
        pass
    
    return rpc
    
def _decodeError(rawRPC, addressPort):
    """
    Decode a KRPC error into a KRPC error object.
    """
    rpc = KRPCError()
    rpc.transactionID = rawRPC[b't']
    rpc.toNode = AppState.thisNode
    
    (address, port) = addressPort

    try:
        (originalQuery, toNode, timestamp) = AppState.outstandingQueries[rpc.transactionID]
    except:
        raise Exception('No matching outstanding query transaction ID could be found.')
        
    if toNode.address != address or toNode.port != port:
        raise Exception('Matching query was sent to a different address or port than this response originated from.')
    
    rpc.type = originalQuery.type
    
    rpc.errorCode = int(rawRPC[b'e'][0])
    rpc.errorMessage = str(rawRPC[b'e'][1])
        
    return rpc
        
def _decodeAddressPortInfo(compactAddressPortString):
    """
    Decode IP-address/port info that is encoded as a
    compact IP-address/port info string.
    """
    
    # Decode address represented as as a 6-byte string
    # https://docs.python.org/2/library/struct.html
    # Format >4sH: 
    # >   - Format using big endian (network byte order)
    # 4s  - ip address takes 4 bytes
    # H   - ports are unsigned shorts (16 bits; max value of 65535)
    (ipBytes, port) = struct.unpack('>4sH', compactAddressPortString)
    
    return (inet_ntoa(ipBytes), port)
    
def _decodePeer(compactPeerString):
    return Peer(_decodeAddressPortInfo(compactPeerString))

def _decodePeers(compactPeersStringList):
    """
    Decode peers that are encoded as a list of
    compact IP-address/port info strings.
    """
    return map(_decodePeer, compactPeersStringList)
    
def _decodeNodeInfo(compactNodeString):
    """
    Decode a node that is encoded as a compact node string.
    """
    nodeID = Hash(compactNodeString[0:20])
    
    (host, port) = _decodeAddressPortInfo(compactNodeString[20:26])
    
    return Node(nodeID, (host, port))
    
def _decodeNodesInfo(compactNodesString):
    """
    Decode nodes that are encoded as a compact nodes info string.
    """
    nodeChunks = utils.chunks(compactNodesString, 26)
    
    return map(_decodeNodeInfo, nodeChunks)
   
def encode(krpcMessage):
    """
    Encode a KRPC message.
    """
    if isinstance(krpcMessage, KRPCQuery):
        encoded = _encodeQuery(krpcMessage)
    elif isinstance(krpcMessage, KRPCResponse):
        encoded = _encodeResponse(krpcMessage)
    elif isinstance(krpcMessage, KRPCError):
        encoded = _encodeError(krpcMessage)
        
    return encoded

def _encodeQuery(krpcQuery):
    """
    Encode a KRPC query.
    """
    if krpcQuery.type == b'ping':
        query = {
            't': krpcQuery.transactionID,
            'y': 'q',
            'q': 'ping',
            'a': {
                'id': bytes(krpcQuery.fromNode)
            }
        }
    elif krpcQuery.type == b'find_node':
        query = {
            't': krpcQuery.transactionID,
            'y': 'q',
            'q': 'find_node',
            'a': {
                'id': bytes(krpcQuery.fromNode),
                'target': krpcQuery.targetID
            }
        }
    elif krpcQuery.type == b'get_peers':
        query = {
            't': str(krpcQuery.transactionID),
            'y': 'q',
            'q': 'get_peers',
            'a': {
                'id': bytes(krpcQuery.fromNode),
                'info_hash': krpcQuery.targetID
            }
        }
    elif krpcQuery.type == b'announce_peer':
        (address, port) = krpcQuery.peer
        if rpc.impliedPort == True:
            query = {
                't': krpcQuery.transactionID,
                'y': 'q',
                'q': 'announce_peer',
                'a': {
                    'id': bytes(krpcQuery.fromNode),
                    'implied_port': 1,
                    'info_hash': krpcQuery.targetID,
                    'port': port,
                    'token': bytes(krpcQuery.token)
                }
            }
        else:
            query = {
                't': str(krpcQuery.transactionID),
                'y': 'q',
                'q': 'announce_peer',
                'a': {
                    'id': bytes(krpcQuery.fromNode),
                    'info_hash': krpcQuery.targetID,
                    'port': port,
                    'token': bytes(krpcQuery.token)
                }
            }
        
    return bencodepy.encode(query)
    
def _encodeResponse(krpcResponse):
    """
    Encode a KRPC response.
    """
    if krpcResponse.type == b'ping':
        response = {
            't': krpcResponse.transactionID,
            'y': 'r',
            'r': {
                'id': bytes(krpcResponse.fromNode)
            }
        }
    elif krpcResponse.type == b'find_node':
        response = {
            't': krpcResponse.transactionID,
            'y': 'r',
            'r': {
                'id': bytes(krpcResponse.fromNode),
                'nodes': _encodeNodes(krpcResponse.nodes)
            }
        }
    elif krpcResponse.type == b'get_peers':
        if krpcResponse.peers != None:
            response = {
                't': krpcResponse.transactionID,
                'y': 'r',
                'r': {
                    'id': bytes(krpcResponse.fromNode),
                    'token': bytes(krpcResponse.token),
                    'values': _encodePeers(krpcResponse.peers)
                }
            }   
        else:
            response = {
                't': krpcResponse.transactionID,
                'y': 'r',
                'r': {
                    'id': bytes(krpcResponse.fromNode),
                    'token': bytes(krpcResponse.token),
                    'nodes': _encodeNodes(krpcResponse.nodes)
                }
            }
    elif krpcResponse.type == b'announce_peer':
        response = {
            't': krpcResponse.transactionID,
            'y': 'r',
            'r': {
                'id': bytes(krpcResponse.fromNode)
            }
        }
        
    return bencodepy.encode(response)
   
def _encodeError(krpcError):
    """
    Encode a KRPC error message.
    """
    error = {
        't': krpcError.transactionID,
        'y': 'e',
        'e': [krpcError.errorCode, krpcError.errorMessage]
    }
    
    return bencodepy.encode(error)
    
def _encodeAddressPortInfo(addressPort):
    """
    Encode an IP and port as a 6-byte string.
    """
    # Represent the host as a string of 6 bytes.
    # https://docs.python.org/2/library/struct.html
    # Format >4sH: 
    # >   - Format using big endian (network byte order)
    # 4s  - inet_aton returns the ip as a string of 4 chars (1 byte per char)
    # H   - ports are unsigned shorts (16 bits; max value of 65535)
    (address, port) = addressPort

    return struct.pack('>4sH', inet_aton(address), port)
        
def _encodePeer(peer):
    """
    Encode a peer as a 6-byte string.
    """
    return _encodeAddressPortInfo(peer.host)
        
def _encodePeers(peers):
    """
    Encode a list of peers as a list of 6-byte strings.
    """
    return functools.reduce(lambda acc, peer: acc + _encodePeer(peer), peers, b"")
        
def _encodeNode(node):
    """
    Encode a node as a 26-byte string (20-byte ID and 6-byte address + port information).
    """
    return str(node.id) + _encodeAddressPortInfo(node.host)

def _encodeNodes(nodes):
    """
    Encode a list of nodes as a string of concatenated encodings of the nodes.
    """
    return functools.reduce(lambda acc, node: acc + _encodeNode(node), nodes, "")
   
class _KRPC():
    """
    Class representing a KRPC message.
    
    Each message has a transaction ID.
    """
    def __init__(self, transactionID, fromNode, toNode):
        self.transactionID = transactionID
        self.fromNode = fromNode
        self.toNode = toNode
        
class KRPCQuery(_KRPC):
    """
    Class representing a KRPC query.
    
    There are four types of KRPC queries: 
     - ping;
     - find_node;
     - get_peers; and
     - announce_peer.
     
    Each query type has a transaction ID (that should be sent back in a response) 
    and an arguments dictionary containing at least the querying node's ID.
    
    Some query types have additional arguments:
    - find_node:
        - target: the ID of the node that is sought
    - get_peers:
        - info_hash: the ID (info_hash) of the torrent that is sought
    - announce_peer:
        - info_hash: the ID (info_hash) of the torrent that a peer is added for
        - port: the port the peer is listening on
        - token: the token sent by a previous get_peers response
        - implied_port (optional): if set and equal to '1' the port argument should be
        ignored the source port of the UDP packet should be used as the peer's listening 
        port.  
    """
    def __init__(self, transactionID=None, fromNode=None, toNode=None, type=None, targetID=None, token=None, peer=None, impliedPort=None, noSeeders=False, scrape=False):
        _KRPC.__init__(self, transactionID, fromNode, toNode)
        
        self.type = type # ping, find_node, get_peers, announce_peer
        self.targetID = targetID
        self.token = token
        self.peer = peer
        self.impliedPort = impliedPort
        self.noSeeders = noSeeders
        self.scrape = scrape
        
    def __repr__(self):
        return "KRPCQuery(transactionID=%r,fromNode=%r,toNode=%r,type=%r,targetID=%r,token=%r,peer=%r,impliedPort=%r,noSeeders=%r,scrape=%r)" % (self.transactionID, self.fromNode, self.toNode, self.type, self.targetID, self.token, self.peer, self.impliedPort, self.noSeeders, self.scrape)
           
        
class KRPCResponse(_KRPC):
    """
    Class representing a KRPC response to a query.
    
    There are four types of KRPC responses:
    - ping;
    - find_node;
    - get_peers; and
    - announce_peer.
    
    The response type is implicitly known through the included transaction ID,
    which was set by the querying node and is copied in the response.
    
    Some response types have additional arguments:
    - find_node:
        - nodes: target node or K closest good nodes
    - get_peers:
        - token: a token generated that has to be returned on a future announce_peer query
        - one of:
            - values: list of K peers
            - nodes: list of K closest good nodes
    """
    def __init__(self, transactionID=None, fromNode=None, toNode=None, responseTo=None, type=None, nodes=None, token=None, peers=None):
        _KRPC.__init__(self, transactionID, fromNode, toNode)
        
        self.responseTo = responseTo
        self.type = type # ping, find_node, get_peers, announce_peer
        self.nodes = nodes
        self.token = token
        self.peers = peers
        
    @staticmethod
    def fromQuery(query):
        """
        Build a bare response from the given query:
        - transaction ID;
        - from node (i.e., this node);
        - to node (i.e., query from node); 
        - query this is a response to; and
        - response type.
        """
        return KRPCResponse(
            transactionID=query.transactionID, 
            fromNode=AppState.thisNode, 
            toNode=query.fromNode,
            responseTo=query,
            type=query.type)
        
    def __repr__(self):
        return "KRPCResponse(transactionID=%r,fromNode=%r,toNode=%r,responseTo=%r,type=%r,nodes=%r,token=%r,peers=%r)" % (self.transactionID, self.fromNode, self.toNode, self.type, self.nodes, self.token, self.peers)
        
class KRPCError(_KRPC):
    """
    Class representing a KRPC error message.
    
    There are four types of KRPC errors:
    - ping;
    - find_node;
    - get_peers; and
    - announce_peer.
    
    The error type is implicitly known through the included transaction ID,
    which was set by the querying node and is copied in the error packet.
    
    Each error contains a transaction ID and an error encoded in a list.
    
    The first element of the list is the error code, one of:
    - 201: generic error;
    - 202: server error;
    - 203: protocol error; and
    - 204: unknown method.
    
    The second element of the list is an error message.
    """
    def __init__(self, transactionID=None, toNode=None, type=None, errorCode=None, errorMessage=None):
        _KRPC.__init__(self, transactionID, None, toNode)
        
        self.type = type
        self.errorCode = errorCode
        self.errorMessage = errorMessage

    @staticmethod
    def fromQuery(query, errorCode=201, errorMessage="A generic error occurred"):
        """
        Build a bare error from the given query:
        - transaction ID;
        - to node (i.e., query from node); 
        - query this is a response to; and
        - response type.
        """
        return KRPCError(
            transactionID=query.transactionID,
            toNode=query.fromNode,
            type=query.type,
            errorCode=errorCode,
            errorMessage=errorMessage)
        
    def __repr__(self):
        return "KRPCError(transactionID=%r,toNode=%r,type=%r,errorCode=%r,errorMessage=%r)" % (self.transactionID, self.toNode, self.type, self.errorCode, self.errorMessage)