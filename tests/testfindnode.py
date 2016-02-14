import bencodepy
import hashlib

import struct

from socket import gethostbyname 
from socket import inet_aton
from socket import inet_ntoa

import twisted.names.client
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class DHTTester(DatagramProtocol):
    def startProtocol(self):
        data = {
            'y': 'q',
            'q': 'find_node',
            'a': {
                'id': hashlib.sha1(b'bla').digest(),
                'target': hashlib.sha1(b'bla2').digest()
            },
            't': b'44'
        }
        
        
        self.transport.write(bencodepy.encode(data), ('127.0.0.1', 8043))
        print("Sent find node")
        
    def datagramReceived(self, data, addressPort):
        (address, port) = addressPort
        print("Datagram %s received from %s" % (repr(data), repr((address, port))))
        
        print(bencodepy.decode(data))
        
        
reactor.listenUDP(8044, DHTTester())
reactor.run()