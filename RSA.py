from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP

class Crpto():
    def __init__(self):
        self._local_key = RSA.generate(1024,Random.new().read)
        self._local_cipher = PKCS1_OAEP.new(self._local_key)

    def getPublicKey(self):
        return self._local_key.publickey().exportKey()

    def setPublicKey(self,key):
        self._dist_key = RSA.importKey(key)
        self._dist_cipher = PKCS1_OAEP.new(self._dist_key)

    def encrypt(self,plain_text):
        "text must be a bytes str \nReturn a bytes str"
        return self._dist_cipher.encrypt(plain_text)

    def decrypt(self,cipher_text):
        "cipher_text must be a bytes str \n Retunr a bytes str"
        return self._local_cipher.decrypt(plain_text)
