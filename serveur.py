from socketTools import *
from tools import *
from socket import *
from account import *
from limFile import *
from time import sleep
import threading
#=============================
class ClientThread(threading.Thread):
    def __init__(self,client,account,clients):
        threading.Thread.__init__(self)
        self.client = client
        self.connected = True
        self.account=account
        self.clients=clients
        
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
                    msg=msg.split(";")
                    print(msg)
                    if msg[0]=="<|ACCOUNT|>":
                        if msg[1]=="<|AUTH|>":
                            tmp=self.account.check(msg[2],msg[3])
                            print(tmp)
                            if tmp==True:
                                self.client.send(b'<|AUTH|>;<|ACCEPTED|>')
                            else:
                                client.send(b'<|AUTH|>;<|REJECTED|>')
                        elif msg[1]=="<|CREATE|>":
                            if self.account.crate(msg[2],msg[3])==True:
                                self.client.send(b'<|ACCOUNT|>;<|CREATE|>;DONE')
                            else:
                                self.client.send(b'<|ACCOUNT|>;<|CREATE|>;EXIST')
                    elif msg[0]=="<|MESSAGE|>":
                        with LimFile("historique.txt",100) as file:
                            file.write(msg[1]+";"+msg[2])
                        self.clients.sendAll(bytes(msg[1]+";"+msg[2],"UTF-8"))
                    elif msg[0]=="<|HISTORIQUE|>":
                        with open("historique.txt","r") as file:
                            for line in file:
                                self.clients.sendAll(bytes(line,"UTF-8"))
                                sleep(1/1000)
        except ConnectionResetError:
            self.connected = False
            pass
        else:
            pass
#-----------------------------
class MultiClient():
    def __init__(self):
        self._clientList=[]

    def addClient(self,client):
        self._clientList.append(client)

    def sendAll(self,msg):
        tmp=[]
        for client in self._clientList:
            if client.connected == True:
                client.send(bytes(msg,"UTF-8"))
            else:
                tmp.append(client)
        for client in tmp:
            self._clientList.remove(client)
#=============================
def init():
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind((myip(),1948))
    account = Account("account.db")
    clients = MultiClient()
    if account.statu()=="No file":
        raise FileNotFoundError("No account.db file")
    print(myip())
    print("1948")
    return server,account,clients
#===============================================
#===============================================
server,account,clients = init()
while True:
    #################################################
    while True:#Connecte le client
        client,adresse = serverAccept(server)
        if client!=False:
            print("Connection to a client")
            newthread = ClientThread(client,account,clients)
            clients.addClient(client)
            newthread.start()
    
