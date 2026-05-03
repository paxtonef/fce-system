from fce.engine import Engine

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = Engine()
    return _engine
