from appstate import AppState
import bloom

from krpc.krpc import KRPC
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

# h1 = Hash(hashlib.sha1("test").digest())
# h2 = Hash(hashlib.sha1("test").digest())
# h3 = Hash(hashlib.sha1("test2").digest())
# print h2.distance(h3)

AppState.prepare()
reactor.listenUDP(AppState.thisNode.port(), KRPC())
#reactor.callLater(3, AppState.routingTable.refresh)
reactor.callLater(3, AppState.routingTable.refresh, (reactor))
reactor.run()
print('test')