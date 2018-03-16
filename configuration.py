#Config file manager by Rémi Audrezet     #
#=========================================#
#                                         #
#=========================================#
#IMPORTATIONS DES LIBRAIRIES ET MODULES====
import os, tools, sys
#DEFINITON DES FONCTIONS===================

#INITIALISATION DES CLASSES================
class Config():

    def __init__(self,path=""):
        self.configDic={}
        self._typeDic={}
        self._comment={}
        self._toLog=""
        self._VALID_TYPES=["str","int","bool"]
        if path != "":
            self.setFile(path)

    def _saveFile(self):
        with open(self._path,"w") as file:
            for key in self.configDic:
                try:
                    for line in self._comment[key]:
                        file.write(line+"�\n")
                except KeyError:
                    pass
                file.write(self._typeDic[key]+";"+key+";"+str(self.configDic[key])+"\n")
            file.close()
            try:
                self.log.write("CONFIG_FILE","save complete")
            except:
                pass

    def setFile(self,path):
        if path[0]!="/":
            path=os.getcwd()+"/"+path
        print(path)
        if os.path.exists(path) and os.path.isdir(path)==False:
            self._path=path
            self._readConf()
            return True
        else:
            return False

    def setLog(self,obj):
        self.log=obj
        if self._toLog!="":
            for tmp in self._toLog:
                self.log.write("CONFIG_FILE",str(tmp))

    def _readConf(self):
        with open(self._path,"r") as file:
            i=1
            tmp=[]
            for line in file:
                line=line.strip()
                if line[0]!="#":
                    content=line.split(";")
                    if content[0]=="str":
                        self.configDic[content[1]]=str(content[2])
                        self._typeDic[content[1]]=str(content[0])
                    elif content[0]=="int":
                        self.configDic[content[1]]=int(content[2])
                        self._typeDic[content[1]]=str(content[0])
                    elif content[0]=="bool":
                        self.configDic[content[1]]=bool(tools.str_to_bool(content[2]))
                        self._typeDic[content[1]]=str(content[0])
                    else:
                        self._toLog.append(line+"at line "+str(i)+" have an incorect data type")
                    self._comment[content[1]]=tmp
                    tmp=[]
                else:
                    tmp.append(line)
            file.close()

    def setConf(self,the_type,name,value):
        try:
            self._VALID_TYPES.index(the_type)
            try:
                self.configDic[name]=value
                self._typeDic[name]=the_type
                self._saveFile()
                return True
            except:
                return False
        except ValueError:
            return False
#==========================================
if __name__=="__main__":
    c=Config()
    print("c=Config()")
