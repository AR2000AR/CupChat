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
LOG_INFO=1
LOG_RX=2
LOG_TX=2
LOG_AUTH=3
LOG_CONF=4
#=============================
class ClientThread(threading.Thread):
    def __init__(self,client,account,clients,config):
        threading.Thread.__init__(self)
        self.client = client
        self.connected = True
        self.account=account
        self.clients=clients
        self.config=config

    def log(self,name,content,lv):
        if self.config.configDic["LOG_LV"]>=lv:
            self.config.log.write(name,content)
        
    def run(self):
        try:
            while self.connected == True:
                msg = reciveMsg(self.client,1024,theType=str)
                ####Gestion des erreurs
                if msg == False:
                    self.connected = False
                    break
                elif msg == "" or msg ==b'':
                    self.connected = False
                    break
                #------------------------------
                else:
                    if msg.split()[0]!="<|ACCOUNT|>":
                        self.log("RX",msg,LOG_RX)
                    msg=msg.split(";")
                    ###Gestion de l'authentification
                    if msg[0]=="<|ACCOUNT|>":
                        #Authentification
                        if msg[1]=="<|AUTH|>":
                            tmp=self.account.check(msg[2],msg[3])
                            if tmp==True:
                                self.client.send(b'<|AUTH|>;<|ACCEPTED|>')
                                self.log("AUTH","ACCEPTED",LOG_AUTH)
                            else:
                                client.send(b'<|AUTH|>;<|REJECTED|>')
                                self.log("AUTH","REJECTED",LOG_AUTH)
                        #Création d'un compte
                        elif msg[1]=="<|CREATE|>":
                            self.log("AUTH","CREATE?",LOG_AUTH)
                            if self.account.create(msg[2],msg[3])==True:
                                self.log("CREATE","DONE",LOG_AUTH)
                                self.client.send(b'<|ACCOUNT|>;<|CREATE|>;DONE')
                            else:
                                self.log("CREATE","EXIST",LOG_AUTH)
                                self.client.send(b'<|ACCOUNT|>;<|CREATE|>;EXIST')
                                
                    ###Envoi de messages
                    elif msg[0]=="<|MESSAGE|>":
                        with LimFile("historique.txt",100) as file:#Ouvre le fichier d'historique avec la classe
                            file.write(msg[1]+";"+msg[2])          #LimFile qui limite la taille de celui ci
                        self.clients.sendAll(bytes(msg[1]+";"+msg[2],"UTF-8"))

                    ###Envoi de l'historique
                    elif msg[0]=="<|HISTORIQUE|>":
                        with open("historique.txt","r") as file:
                            for line in file:
                                self.clients.sendAll(bytes(line,"UTF-8"))
                                sleep(1/1000)
        except ConnectionResetError:
            log("DECONNECTON","Client déconécté",LOG_INFO)
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
    "Fonction désiné à initialisé le serveur"
    ###Charge les config
    config = Config("config.cfg")
    log = Log("log.txt",config.configDic["LOG"],mode=LOG_REPLACE)
    config.setLog(log)
    #Démare le serveur
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind((myip(),config.configDic["PORT"]))
    ###Ouvre la base de donée des comptes
    account = Account("account.db")
    ###Prépare l'acceuil de multiples clients
    clients = MultiClient()
    if account.statu()=="No file":#Verifie l'existence de la base de donné
        log.write("CRITICAL","No account.db file")
        raise FileNotFoundError("No account.db file")
    ###Affiche est journalise les info concernant l'initialisation
    print("ip:"+myip())
    print("port:"+str(config.configDic["PORT"]))
    config.log.write("INI",str(myip()))
    config.log.write("INI",str(config.configDic["PORT"]))
    if config.configDic["LOG_LV"]>=LOG_CONF:
        for item in config.configDic:
            config.log.write("CONFIG",item+":"+str(config.configDic[item]))
    ###Renvoie le résultat de l'initialisation
    return server,account,clients,config
#===============================================
#===============================================
server,account,clients,config = init()#Initialise le serveur

while True:
    client,adresse = serverAccept(server)#Connecte le client
    if client!=False:
        if config.configDic["LOG_LV"]>=LOG_INFO:
            config.log.write("CONNECTION","Connection to a client")
        ###Démare une nouvelle tache
        newthread = ClientThread(client,account,clients,config)
        clients.addClient(client)
        newthread.start()
#=============================================
