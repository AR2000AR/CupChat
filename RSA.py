from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP

class Crypto():
    def __init__(self):
        self._local_key = RSA.generate(1024,Random.new().read)
        self._local_cipher = PKCS1_OAEP.new(self._local_key)

    def getPublicKey(self):
        return self._local_key.publickey().exportKey()

    def setPublicKey(self,key):
        self._dist_key = RSA.importKey(key)
        self._dist_cipher = PKCS1_OAEP.new(self._dist_key)

    def encrypt(self,plain_text):
        "Return a bytes str"
        if type(plain_text)==str:
            plain_text=bytes(plain_text,"UTF-8")
        return self._dist_cipher.encrypt(plain_text)

    def decrypt(self,cipher_text):
        "Retunr a bytes str"
        if type(cipher_text)==str:
            cipher_text=bytes(cipher_text,"UTF-8")
        return self._local_cipher.decrypt(plain_text)
