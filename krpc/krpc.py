"""
@author Thomas Churchman

Module that processes and sends KRPC messages.
"""

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

from appstate import AppState
import utils
import krpc.krpccoder
from dht.node import Node

class KRPC(DatagramProtocol):
    """
    Handles sending and receiving KRPC messages.
    
    Example: https://github.com/gsko/mdht/blob/master/mdht/protocols/krpc_sender.py
    """
    def datagramReceived(self, data, addressPort):
        """
        Called by Twisted.
        """
        (address, port) = addressPort

        print("received %r from %s:%d" % (data, address, port))

        try:
            message = krpc.krpccoder.decode(data, (address, port))
            print(message)
        except:
            print("received malformed packet")
            return
            
        self._krpcReceived(message)
           
    def _krpcReceived(self, krpcMessage):
        """
        Process a KRPC message.
        """
        if isinstance(krpcMessage, krpc.krpccoder.KRPCQuery):
            self.__krpcQueryReceived(krpcMessage)
        elif isinstance(krpcMessage, krpc.krpccoder.KRPCResponse):
            self.__krpcResponseReceived(krpcMessage)
        elif isinstance(krpcMessage, krpc.krpccoder.KRPCError):
            self.__krpcErrorReceived(krpcMessage)
            
    def __krpcQueryReceived(self, krpcQuery):
        """
        Process a KRPC query.
        """
        if krpcQuery.type == b'ping':
            self.__krpcQueryPingReceived(krpcQuery)
        elif krpcQuery.type == b'find_node':
            self.__krpcQueryFindNodeReceived(krpcQuery)
        elif krpcQuery.type == b'get_peers':
            self.__krpcQueryGetPeersReceived(krpcQuery)
        elif krpcQuery.type == b'announce_peer':
            self.__krpcQueryAnnouncePeerReceived(krpcQuery)
        
    def __krpcResponseReceived(self, krpcResponse):
        pass
        
    def __krpcErrorReceived(self, krpcError):
        pass
        
    def __krpcQueryPingReceived(self, krpcQuery):
        """
        Process a KRPC ping query.
        """
        response = krpc.krpccoder.KRPCResponse.fromQuery(krpcQuery)
        self._krpcSend(response)
        
    def __krpcQueryFindNodeReceived(self, krpcQuery):
        """
        Process a find_node query.
        """
        response = krpc.krpccoder.KRPCResponse.fromQuery(krpcQuery)

        target = krpcQuery.targetID
        targetNode = AppState.routingTable.findNode(target)

        if targetNode:
            response.nodes = [targetNode]
        else:
            kClosestTargets = AppState.routingTable.findClosestNodes(target)
            response.nodes = kClosestTargets

        self._krpcSend(response)
            
        
    def __krpcQueryGetPeersReceived(self, krpcQuery):
        """
        Process a KRPC get_peers query.
        """
        response = krpc.krpccoder.KRPCResponse.fromQuery(krpcQuery)
        response.token = utils.getToken(krpcQuery.fromNode)
        
        if AppState.peerStorage.torrentExists(krpcQuery.targetID):
            peers = AppState.peerStorage.getPeers(krpcQuery.targetID)
            if krpcQuery.noSeeders:
                peers = filter(lambda p: not p.seeder, peers)
            response.peers = AppState.peerStorage.getPeers(krpcQuery.targetID)
        else:
            response.nodes = AppState.routingTable.findClosestNodes(krpcQuery.targetID)
            
        self._krpcSend(response)
            
    def __krpcQueryAnnouncePeerReceived(self, krpcQuery):
        """
        Process a KRPC announce peer query.
        """
        if utils.isTokenValid(krpcQuery.fromNode, krpcQuery.token):
            AppState.peerStorage.addPeer(krpcQuery.targetID, krpcQuery.peer)
            response = krpc.krpccoder.KRPCResponse.fromQuery(krpcQuery)
        else:
            response = krpc.krpccoder.KRPCError.fromQuery(krpcQuery, errorCode=203, errorMessage=b"Invalid token")

        self._krpcSend(response)
        
    def _krpcSend(self, krpcMessage):
        if isinstance(krpcMessage, krpc.krpccoder.KRPCQuery):
            self.__krpcSendQuery(krpcMessage)
        elif isinstance(krpcMessage, krpc.krpccoder.KRPCResponse):
            self.__krpcSendResponse(krpcMessage)
        elif isinstance(krpcMessage, krpc.krpccoder.KRPCError):
            self.__krpcSendError(krpcMessage)
        
    def __krpcSendQuery(self, krpcQuery):
        query = krpc.krpccoder.encode(krpcQuery)
        self.transport.write(query, krpcQuery.toNode.host)
        
        
    def __krpcSendResponse(self, krpcResponse):
        response = krpc.krpccoder.encode(krpcResponse)
        self.transport.write(response, krpcResponse.toNode.host)
    
    def __krpcSendError(self, krpcError):
        error = krpc.krpccoder.encode(krpcError)
        self.transport.write(error, krpcError.toNode.host)
        