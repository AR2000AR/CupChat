#ACCOUNT MANAGMENT MODULE   #
#By Rémi Audrézet           #
#############################
import os
import hashlib
from Crypto import Random
#============================
class Account():
    def __init__(self,file=""):
        self._file=""
        self._random = Random.new()
        if file != "":
            self.openFile(file)

    def openFile(self,file):
        if os.path.exists(file) and os.path.isfile(file):
            self._file=file

    def check(self,name,password):
        with open(self._file,"r") as db:
            for item in db:
                item=item.split(";")
                if item[0]==hashlib.md5(name.encode()).hexdigest():
                    if item[2].strip()==hashlib.md5(item[1].encode()+password.encode()).hexdigest():
                        return True
            return False
        
    def exist(self,name):
        with open(self._file,"r") as db:
            for item in db:
                item=item.split(";")
                if item[0]==hashlib.md5(name.encode()).hexdigest():
                    return True
            return False

    def create(self,name,password):
        if self.exist(name)==True:
            return False
        else:
            with open(self._file,"a") as db:
                salt=self._random.read(128).hex()
                db.write(hashlib.md5(name.encode()).hexdigest()+";"+salt+";"+hashlib.md5(salt.encode()+password.encode()).hexdigest()+"\n")
            return True

    def statu(self):
        if self._file=="":
            return "No file"
        else:
            return "OK"
                
if __name__ == "__main__":
    a=Account("t.db")
