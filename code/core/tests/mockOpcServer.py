import socket
import time
import threading

TCP_IP = "127.0.0.1"
TCP_PORT = 7890
BUFFER_SIZE = 1024

sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_STREAM) # UDP

def server():
    sock.bind((TCP_IP, TCP_PORT))
    sock.listen(1)
    conn, addr = sock.accept()

    while True:
        data = conn.recv(BUFFER_SIZE) # buffer size is 1024 bytes
        conn.send("Thanks")

    conn.close()

def run_server():
    thread = threading.Thread(target=server)
    thread.daemon = True
    thread.start()

    #TODO Clean this up
    time.sleep(1)
    print "running mock opc server...."


if __name__ == '__main__':

    run_server()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send("SERVER")
    data = s.recv(BUFFER_SIZE)
    s.close()
