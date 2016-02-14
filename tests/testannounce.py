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
            'q': 'get_peers',
            'a': {
                'id': hashlib.sha1(b'bla').digest(),
                'info_hash': hashlib.sha1(b'someTorrent').digest()
            },
            't': b'42'
        }
        
        self.transport.write(bencodepy.encode(data), ('127.0.0.1', 8043))
        
        print("Sent get_peers")
        
    def datagramReceived(self, data, addressPort):
        (address, port) = addressPort
        print("Datagram %s received from %s" % (repr(data), repr((address, port))))
        
        data = bencodepy.decode(data)
        if data[b'y'] == b'r' and data[b't'] == b'42':
            token = data[b'r'][b'token']
            newData = {
                'y': 'q',
                'q': 'announce_peer',
                'a': {
                    'id': hashlib.sha1(b'bla').digest(),
                    'info_hash': hashlib.sha1(b'someTorrent').digest(),
                    'port': 8046,
                    'token': token
                },
                't': b'43'
            }
            
            self.transport.write(bencodepy.encode(newData), ('127.0.0.1', 8043))
            
            print("Sent announce")
        
reactor.listenUDP(8044, DHTTester())
reactor.run()