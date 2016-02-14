"""
@author Thomas Churchman
"""

import os.path
import struct
from socket import inet_ntoa
from socket import inet_aton

import utils
import appstate
from dht.peer import Peer

class _PeerStorage:
    """
    Class to represent a Peer Storage. 
    Handles database interaction.
    """
    
    def __init__(self):
        pass
        
class MySQLPeerStorage(_PeerStorage):
    """
    Stores peers in and reads peers from a MySQL database.
    """
    def __init__(self):
        _PeerStorage.__init__(self)
    
class FilePeerStorage(_PeerStorage):
    """
    Stores peers in and reads peers from files on the disk.
    """
    def __init__(self, storageDir):
        _PeerStorage.__init__(self)
        self.storageDir = storageDir
    
    def _filePath(self, hash):
        return os.path.join(self.storageDir, hex(int(hash)))
    
    def _decodePeerInfo(self, str):    
        # Decode peer represented as as a 7-byte string
        # https://docs.python.org/2/library/struct.html
        # Format >4sH?: 
        # >   - Format using big endian (network byte order)
        # 4s  - ip address takes 4 bytes
        # H   - ports are unsigned shorts (16 bits; max value of 65535)
        # ?   - bool indicating whether the peer is a seeder (true) or a leecher (false)
        (ipBytes, port, seeder) = struct.unpack('>4sH?', str)
        
        return Peer((inet_ntoa(ipBytes), port), seeder)
    
    def _decodePeersInfo(self, str):
        """
        Decode all peers.
        """
        peers = utils.chunks(str, 7)
        peers = map(self._decodePeerInfo, peers)
        
        return list(peers)
    
    def _encodePeerInfo(self, peer):
        # Encode peer represented as as a 7-byte string
        # https://docs.python.org/2/library/struct.html
        # Format >4sH?: 
        # >   - Format using big endian (network byte order)
        # 4s  - ip address takes 4 bytes
        # H   - ports are unsigned shorts (16 bits; max value of 65535)
        # ?   - bool indicating whether the peer is a seeder (true) or a leecher (false)
        str = struct.pack('>4sH?', inet_aton(peer.address()), peer.port(), peer.seeder)
        
        return str
        
    def torrentExists(self, hash):
        """
        Check if we are tracking the given torrent hash
        """
        filePath = self._filePath(hash)
        return os.path.isfile(filePath)
        
    def getPeers(self, hash):
        """
        Get the peers associated with the given torrent
        """
        if not self.torrentExists(hash):
            raise Exception('That torrent is not tracked')
        filePath = self._filePath(hash)
        
        f = open(filePath, 'rb')
        str = f.read()
        f.close()
        return self._decodePeersInfo(str)
        
    def addPeer(self, hash, peer):
        """
        Add a peer to the given torrent.
        Create the torrent if it is not tracked yet.
        """
        filePath = self._filePath(hash)
        if not self.torrentExists(hash):
            peers = []
            f = open(filePath, 'wb')
        else:
            peers = self.getPeers(hash)
            f = open(filePath, 'ab')
        
        if peer in peers or len(peers) >= appstate.AppState.maxPeersPerTorrent:
            added = False
        else:
            f.write(self._encodePeerInfo(peer))
            added = True
            
        f.close()
        return added
        