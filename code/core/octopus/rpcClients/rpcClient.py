import xmlrpclib

class RpcClient:
    def __init__(self, host="http://127.0.0.1:8000"):
        self.host = host
        self.server = xmlrpclib.ServerProxy(self.host)

    def put(self, data):
        try:
            self.server.put(data)
        except Exception:
            print "WARNING: Could not put to", self.host
