#Socket tools by Rémi Audrézet            #
#=========================================#
#                                         #
#=========================================#
#IMPORTATIONS DES LIBRAIRIES ET MODULES====
import tools
from socket import *
#INITIALISATION DES VARIABLES==============
#PSEUDO CONSTANTES=========================
#DEFINITION DES FONCTIONS==================
def serverAccept(socket,log=False):
    "wait until timeout or accept one connection if avaliable"
    log.write("INFO","Waiting for a client to connect...")
    try:
        socket.listen(1)
        client, adresse = socket.accept()
        if log!=False and type(log)!=bool:
            log.write("CONNECTION","Connected to : "+str(adresse))
        return client, adresse
    except timeout as error:
        return False, False
    else:
        pass
#----------------------------------------
#----------------------------------------
def clientConnect(ip="ask",port="ask",log=False,test=False,maxAttemp=1):
    if ip == "ask":
        ip=input("Connect to : ")
    if port == "ask":
        while True:
            i = input("Port : ")
            try:
                port = int(i)
            except ValueError:
                print("Port must be a number")
    ############################################
    client = socket(AF_INET, SOCK_STREAM)
    client.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    client.connect((ip,port))
    if type(test) == str:
        client.send(b'<|TEST|>')
    if log != False:
        log.write("CONNECTION","Connected to ("+ip+":"+str(port)+")")
        if type(test)==str:
            msg = reciveMsg(client,1024,log,maxAttemp,str)
    else:
        if type(test)==str:
            msg = reciveMsg(client,1024,False,maxAttemp,str)
    if type(test) == str:
        msg = msg.split(";")
        if msg[0] == "<|TEST|>" and msg[1] == test:
            if log != False:
                log.write("CONNECTION","Connection tested for : ("+ip+":"+str(port)+")")
            return client,msg[2]
        else:
            client.shutdown(2)
            client.close()
            return False
    else:
        return client
#----------------------------------------
#----------------------------------------
def reciveMsg(socket,buffersize=1024,log=False,maxAttemp=1,theType=bytes):
    "return the socket message. If timeout return \"\" and if the other end is deconnected return False"
    t=0
    while t<maxAttemp:
        try:
            recu = socket.recv(buffersize)
            if recu:
                if theType==bytes:
                    return recu
                elif theType==str:
                    return recu.decode()
                else:
                    raise TypeError("theType must be bytes or str not "+str(theType))
            else:
                if log != False:
                  log.write("DISCONNECTED","The server closed the connection")
                return False
        except timeout as error:
            t=t+1
            if log != False:
              log.write("TRANSMITION_ERROR","Timeout")
            if theType==bytes:
                return b''
            elif theType==str:
                return ""
            else:
                raise TypeError("theType must be bytes or str not "+str(theType))
        else:
            pass
#------------------------------------------
#------------------------------------------
def sendFile(mysocket,path):
    with open(path,"rb") as f:
        mysocket.sendfile(f)
        mysocket.send(b'<|over|>')
#------------------------------------------
#------------------------------------------
def reciveFile(mysocket,path):
    with open(path,"wb") as file:
        file.close()
    while True:
        recu=mysocket.recv(1000000)
        if recu!=b'<|over|>':
            with open(path,"ab") as file:
                file.write(recu)
                file.close()
        else:
            break
#############################################
if __name__=="__main__":
    pass
