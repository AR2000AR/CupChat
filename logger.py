#Logger by Rémi Audrezet                  #
#=========================================#
#                                         #
#=========================================#
#IMPORTATIONS DES LIBRAIRIES ET MODULES====
import os, tools, sys
from time import localtime
#DEFINITON DES FONCTIONS===================

#PSEUDO CONSTANTES=========================
LOG_REPLACE = "replace"
LOG_APPEND = "append"
#INITIALISATION DES CLASSES================
class Log():
    def __init__(self,path="",enable=True,mode=LOG_APPEND):
        if mode==LOG_APPEND or mode==LOG_REPLACE:
            self._mode=mode
        else:
            self._mode=LOG_APPEND
        if type(enable)==bool:
          self._enabled=enable
        if path!="":
            self.open(path)
        else:
            self._enabled=False

    def _buildTimeStamp(self):
        return str(localtime().tm_mday)+"/"+str(localtime().tm_mon)+"/"+str(localtime().tm_year)+"|"+str(localtime().tm_hour)+":"+str(localtime().tm_min)+":"+str(localtime().tm_sec)

    def open(self,path):
        parent=tools.list_to_str(path.split("/")[0:-1],"/")
        try:
            if parent[0]!="/":
                parent=sys.path[0]+"/"+parent
        except:
            parent=sys.path[0]+"/"+parent
        if os.path.exists(parent) and os.path.exists(path) and os.path.isdir(path)==False:
            self._path=path
            if self._mode==LOG_REPLACE:
                file=open(self._path,"w")
                file.close()
            return True
        elif os.path.exists(parent) and os.path.exists(path)==False:
            file=open(path,"w")
            file.close()
            self._path=path
            return True
        else:
            return False

    def enable(self,op):
        if type(op)==bool:
            self._enabled=op
            return True
        else:
            return False
        
    def enabled(self):
        return self._enabled

    def write(self,name,content):
        if self._enabled:
            with open(self._path,"a") as file:
                if name!="":
                    file.write("["+self._buildTimeStamp()+"] <"+name+"> "+content+"\n")
                else:
                    file.write("["+self._buildTimeStamp()+"] "+content+"\n")
                file.close()
#==============================================
if __name__=="__main__":
    l=Log("data/log.txt",True,"replace")
print("l=Log()")
