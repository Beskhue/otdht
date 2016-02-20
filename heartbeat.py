"""
@author Thomas Churchman
"""

from appstate import AppState

def heartbeat(reactor):
    """
    Heartbeat in which to perform periodic tasks, 
    such as keeping the routing table fresh.
    """
    reactor.callLater(AppState.heartbeat, heartbeat, reactor)