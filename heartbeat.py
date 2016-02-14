from appstate import AppState

def heartbeat(reactor):
    reactor.callLater(AppState.heartbeat, heartbeat, reactor)