from rpcClient import RpcClient

#Basic RpcClient that sends key/value pairs from the user
class UserInputClient(RpcClient):
    def run(self):
        while True:
            print '-' * 30
            key = raw_input("Key: ")
            value = raw_input("Value: ")
            self.put({key: value})

if __name__ == '__main__':
    UserInputClient().run()