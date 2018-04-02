from socketTools import *
from tools import *
from socket import *
from account import *
from limFile import *
from time import sleep
from configuration import *
from logger import *
import threading
#=============================
LOG_RX=1
LOG_TX=1
LOG_AUTH=2
#=============================
class ClientThread(threading.Thread):
    def __init__(self,client,account,clients,config):
        threading.Thread.__init__(self)
        self.client = client
        self.connected = True
        self.account=account
        self.clients=clients
        self.config=config
        self.log=config.log
        
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
                    if self.config.configDic["LOG_LV"]>=LOG_RX and msg.split()[0]!="<|ACCOUNT|>":
                        self.log.write("RX",msg)
                    msg=msg.split(";")
                    if msg[0]=="<|ACCOUNT|>":
                        if msg[1]=="<|AUTH|>":
                            tmp=self.account.check(msg[2],msg[3])
                            if tmp==True:
                                self.client.send(b'<|AUTH|>;<|ACCEPTED|>')
                                if self.config.configDic["LOG_LV"]>=LOG_AUTH:
                                    self.log.write("AUTH","ACCEPTED")
                            else:
                                client.send(b'<|AUTH|>;<|REJECTED|>')
                                if self.config.configDic["LOG_LV"]>=LOG_AUTH:
                                    self.log.write("AUTH","REJECTED")
                        elif msg[1]=="<|CREATE|>":
                            if self.config.configDic["LOG_LV"]>=LOG_AUTH:
                                    self.log.write("AUTH","CREATE?")
                            if self.account.create(msg[2],msg[3])==True:
                                if self.config.configDic["LOG_LV"]>=LOG_AUTH:
                                    self.log.write("CREATE","DONE")
                                self.client.send(b'<|ACCOUNT|>;<|CREATE|>;DONE')
                            else:
                                if self.config.configDic["LOG_LV"]>=LOG_AUTH:
                                    self.log.write("CREATE","EXIST")
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
    config = Config("config.cfg")
    log = Log("log.txt",config.configDic["LOG"],mode=LOG_REPLACE)
    config.setLog(log)
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind((myip(),config.configDic["PORT"]))
    account = Account("account.db")
    clients = MultiClient()
    if account.statu()=="No file":
        log.write("CRITICAL","No account.db file")
        raise FileNotFoundError("No account.db file")
    print("ip:"+myip())
    print("port:"+str(config.configDic["PORT"]))
    config.log.write("INI",str(myip()))
    config.log.write("INI",str(config.configDic["PORT"]))
    for item in config.configDic:
        config.log.write("CONFIG",item+":"+str(config.configDic[item]))
    return server,account,clients,config
#===============================================
#===============================================
server,account,clients,config = init()
while True:
    #################################################
    while True:#Connecte le client
        client,adresse = serverAccept(server)
        if client!=False:
            print("Connection to a client")
            config.log.write("CONNECTION","Connection to a client")
            newthread = ClientThread(client,account,clients,config)
            clients.addClient(client)
            newthread.start()
    
