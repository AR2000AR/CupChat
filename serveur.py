from socketTools import *
from tools import *
from socket import *
from account import *
from limFile import *
from time import sleep
from configuration import *
from logger import *
from RSA import *
import threading
#=============================
LOG_INFO=1
LOG_RX=5
LOG_TX=5
LOG_AUTH=4
LOG_CONF=3
#=============================
class ClientThread(threading.Thread):
    def __init__(self,client,account,clients,config):
        threading.Thread.__init__(self)
        self.client = client
        self.connected = True
        self.account=account
        self.clients=clients
        self.config=config
        self.secue=0
        self.h=LimFile("Data/Serveur/historique.txt",100)#Ouvre le fichier d'historique avec la classe LimFile qui limite la taille de celui ci

    def send(self,msg):
        self.client.send(bytes(str(config.rsa.encrypt(msg)),"UTF-8"))
    
    def log(self,name,content,lv):
        if self.config.configDic["LOG_LV"]>=lv:
            self.config.log.write(name,content)
        
    def run(self):
        try:
            while self.connected == True:
                msg = reciveMsg(self.client,1024,theType=str)
                ####Gestion des erreurs
                if msg == False:
                    self.log("DECONNECTON","Client déconécté",LOG_INFO)
                    self.connected = False
                    self.client.close()
                    self.clients.clear()
                    break
                elif msg=="":
                    pass
                #------------------------------
                else:
                    if self.secure == 0:
                        self.client.send(b'<|CONNECTION|>;'+bytes(config.rsa.getPublicKey(),"UTF-8"))
                        self.secure = 1
                    elif self.secure == 1:
                        msg=msg.split(";")
                        if msg[0] == "<|CONNECTION|>":
                            config.rsa.setPublicKey(msg[1])
                                         
                    else:
                        msg=config.rsa.decrypt(msg)
                        if msg.split()[0]!="<|ACCOUNT|>":
                            self.log("RX",msg,LOG_RX)
                        msg=msg.split(";")
                        ###Gestion de l'authentification
                        if msg[0]=="<|ACCOUNT|>":
                            #Authentification
                            if msg[1]=="<|AUTH|>":
                                tmp=self.account.check(msg[2],msg[3])
                                if tmp==True:
                                    self.send(b'<|AUTH|>;<|ACCEPTED|>')
                                    self.log("AUTH","ACCEPTED",LOG_AUTH)
                                else:
                                    self.send(b'<|AUTH|>;<|REJECTED|>')
                                    self.log("AUTH","REJECTED",LOG_AUTH)
                            #Création d'un compte
                            elif msg[1]=="<|CREATE|>":
                                self.log("AUTH","CREATE?",LOG_AUTH)
                                if self.account.create(msg[2],msg[3])==True:
                                    self.log("CREATE","DONE",LOG_AUTH)
                                    self.send(b'<|ACCOUNT|>;<|CREATE|>;DONE')
                                else:
                                    self.log("CREATE","EXIST",LOG_AUTH)
                                    self.send(b'<|ACCOUNT|>;<|CREATE|>;EXIST')
                                    
                        ###Envoi de messages
                        elif msg[0]=="<|MESSAGE|>":
                            self.h.write(msg[1]+";"+msg[2])
                            self.clients.sendAll("<|MESSAGE|>;"+msg[1]+";"+msg[2])

                        ###Envoi de l'historique
                        elif msg[0]=="<|HISTORIQUE|>":
                            with open("Data/Serveur/historique.txt","r") as file:
                                for line in file:
                                    self.log("TX",line.strip(),LOG_TX)
                                    self.send(bytes("<|MESSAGE|>;"+line.strip(),"UTF-8"))
                                    sleep(1/1000)
        except ConnectionResetError:
            self.log("DECONNECTON","Client déconécté",LOG_INFO)
            self.connected = False
            self.client.close()
            self.clients.clear()
        except OSError:
            self.log("DECONNECTON","Client déconécté",LOG_INFO)
            self.connected = False
            self.client.close()
            self.clients.clear()
        #else:
            #pass
#-----------------------------
class MultiClient():
    def __init__(self,config):
        self._clientList=[]
        self.config=config

    def addClient(self,client):
        self._clientList.append(client)

    def sendAll(self,msg):
        tmp=[]
        for client in self._clientList:
            if client.connected == True:
                if self.config.configDic["LOG_LV"]>=LOG_TX:
                    self.config.log.write("TX",msg)
                client.send(msg)
            else:
                tmp.append(client)
        for client in tmp:
            self._clientList.remove(client)

    def clear(self):
        tmp=[]
        for client in self._clientList:
            if client.connected == False:
                tmp.append(client)
        for client in tmp:
            self._clientList.remove(client)
#=================================================
def init():
    "Fonction désiné à initialisé le serveur"
    test=[False,False]
    ###Charge les config
    if os.path.exists("Data/Serveur/config.cfg") and os.path.isfile("Data/Serveur/config.cfg"):
        pass
    else:
        try:
            os.makedirs("Data")
        except FileExistsError:
            pass
        try:
            os.makedirs("Data/Serveur")
        except FileExistsError:
            pass
        
        with open("Data/Serveur/config.cfg","w") as f:
            f.write("bool;LOG;True\nint;PORT;51648\n#min 0 max 4\nint;LOG_LV;2")
            f.close()
    config = Config("Data/Serveur/config.cfg")
    log = Log("Data/Serveur/log.txt",config.configDic["LOG"],mode=LOG_REPLACE)
    config.setLog(log)
    
    #Démare le serveur
    setdefaulttimeout(2)
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind((myip(),config.configDic["PORT"]))
    
    ###Vérifie l'historique
    if os.path.exists("Data/Serveur/historique.txt") and os.path.isfile("Data/Serveur/historique.txt"):
        pass
    else:
        with open("Data/Serveur/historique.txt","w") as f:
            f.close()
            test[0]=False
            
    ###Ouvre la base de donée des comptes
    if os.path.exists("Data/Serveur/account.db") and os.path.isfile("Data/Serveur/account.db"):
        pass
    else:
        with open("Data/Serveur/account.db","w") as f:
            f.write("*;*\n")
            f.close()
            test[1]=False
    account = Account("Data/Serveur/account.db")

    #Prépare le chiffrement
    config.rsa = Crypto()
    
    ###Prépare l'acceuil de multiples clients
    clients = MultiClient(config)
    if account.statu()=="No file":#Verifie l'existence de la base de donné
        log.write("CRITICAL","No account.db file")
        raise FileNotFoundError("No Data/Serveur/account.db file")
    
    ###Affiche est journalise les info concernant l'initialisation
    config.log.write("INI",str(myip()))
    config.log.write("INI",str(config.configDic["PORT"]))
    config.log.write("INI","WD : "+os.getcwd())
    if test[0]==True:
        config.log.write("INI","historique.txt created")
    if test[0]==True:
        config.log.write("INI","account.db created")
    if config.configDic["LOG_LV"]>=LOG_CONF:
        for item in config.configDic:
            config.log.write("CONFIG",item+":"+str(config.configDic[item]))
    ###Renvoie le résultat de l'initialisation
    return server,account,clients,config
#=================================================
#=================================================
server,account,clients,config = init()#Initialise le serveur

while True:
    client,adresse = serverAccept(server)#Connecte le client
    if client!=False:
        if config.configDic["LOG_LV"]>=LOG_INFO:
            config.log.write("CONNECTION","Connection to a client")
        ###Démare une nouvelle tache
        newthread = ClientThread(client,account,clients,config)
        clients.addClient(newthread)
        newthread.start()
#=============================================
