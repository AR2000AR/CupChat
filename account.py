#ACCOUNT MANAGMENT MODULE   #
#By Rémi Audrézet           #
#############################
import os
import hashlib
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
        with open(self._file,"r") as db:
            for item in db:
                item=item.split(";")
                if item[0]==name:
                    if item[1].strip()==hashlib.md5(password.encode()).hexdigest():
                        return True
            return False
        
    def exist(self,name):
        with open(self._file,"r") as db:
            for item in db:
                item=item.split(";")
                if item[0]==name:
                    return True
            return False

    def create(self,name,password):
        if self.exist(name)==True:
            return False
        else:
            with open(self._file,"a") as db:
                db.write(name+";"+hashlib.md5(password.encode()).hexdigest()+"\n")
            return True

    def statu(self):
        if self._file=="":
            return "No file"
        else:
            return "OK"
                
