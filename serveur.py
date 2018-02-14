from socketTools import *
from tools import *
from socket import *
import threading
#=============================
class ClientThread(threading.Thread):
    def __init__(self,client):
        threading.Thread.__init__(self)
        self.client = client
        self.connected = True
        
    def run(self):
        try:
            while self.connected == True:
                msg = reciveMsg(self.client,1024,theType=str)
                if msg == False:
                    self.connected = False
                    break
                elif msg == "" or msg ==b'':
                    self.connected = False
                    break
                #------------------------------
                else:
                    self.client.send(bytes(msg,"UTF-8"))
                    print(msg)
        except ConnectionResetError:
            self.connected = False
            self.stop
        else:
            self.stop()
#=============================
def init():
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind((myip(),1948))
    print(myip())
    print("1948")
    return server
#===============================================
#===============================================
server = init()
while True:
    #################################################
    while True:#Connecte le client
        client,adresse = serverAccept(server)
        if client!=False:
            print("Connection to a client")
            newthread = ClientThread(client)
            newthread.start()
    
