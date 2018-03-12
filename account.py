#ACCOUNT MANAGMENT MODULE   #
#By Rémi Audrézet           #
#############################
import os
#============================
class Account():
    def __init__(self,file=""):
        self._file=""
        if file != "":
            self.openFile(file)

    def openFile(self,file):
        if os.path.exists(file) and os.path.isfile(file):
            self._file=file

    def check(self,name,password):
        with open(file,"r") as db:
            for item in db:
                item=item.split(";")
                if item[0]==name:
                    if item[1]==password:
                        return True
                    else:
                        return False
                else:
                    return False
        
    def exist(self,name):
        with open(file,"r") as db:
            for item in db:
                item=item.split(";")
                if item[0]==name:
                    return True
                else:
                    return False

    def create(self,name,password):
        if exits(name)==True:
            return False
        else:
            with open(file,"a") as db:
                db.write(name+";"+password+"\n")

    def statu(self):
        if self._file=="":
            return "No file"
                
