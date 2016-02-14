"""
Config file.
"""

import os.path

# UDP port the node listens on
NODE_PORT = 6881

# The name this node's ID is derived from
NODE_ID_NAME = b"An Adequately Random Node Name For Entropy"

# Heartbeat interval in seconds
HEARTBEAT = 3.0

# Bootstrap into the DHT network
BOOTSTRAP = [   ("dht.transmissionbt.com", 6881),
                ("router.utorrent.com", 6881)]

# The external IP of this node
NODE_IP = '0.0.0.0'
                
# Specify which type of peer storage you wish to use.
# One of: file, mysql (currently only file is supported)
PEER_STORAGE = 'file'

# Specify where to store peers (only used for file peer storage)
PEER_STORAGE_DIR = os.path.join('.', 'peer_storage')

# Protocol settings (should not be changed)
K = 8
MAX_NODES_PER_BUCKET = K
MAX_PEERS_PER_TORRENT = 6000