#By Rémi Audrezet                         #
#=========================================#
#                                         #
#=========================================#
#IMPORTATIONS DES LIBRAIRIES ET MODULES====
import socket
#INITIALISATION DES VARIABLES==============
VERSION = "0.1"
#DEFINITION DES FONCTIONS==================
def myip():
    "return the local ip"
    ip=(([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
    if ip == "no IP found":
        return False
    else:
        return ip
#------------------------------------------
def list_to_str(liste,sep=""):
    tmp=""
    for item in liste:
        tmp=tmp+sep+item
    if sep!="":
        return tmp[1:len(tmp)]
    else:
        return tmp
#------------------------------------------
def str_to_bool(string):
    if string=="True":
        return True
    elif string=="False":
        return False
    else:
        pass
#------------------------------------------
def type_to_str(the_type):
    if the_type==str:
        return "str"
    elif the_type==int:
        return "int"
    elif the_type==bool:
        return "bool"
    else:
        return False
#------------------------------------------
def checkCount(nb,maxi):
    "return \"+maxi\" if nb>maxi"
    if nb<=maxi:
        return nb
    else:
        return "+"+str(maxi)
#------------------------------------------
def printFile(path):
    with open(path,"r") as file:
        for line in file:
            print(line.strip())
#DEFINITON DES CLASSES=====================
class InititalisationError(Exception):
    pass
#==========================================
if __name__ == "__main__":
    print(myip())
