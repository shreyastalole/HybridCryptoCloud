from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import os


def DAES(path,key,iv):
    f=open(os.path.join(path+"/Segments","0.txt"),"rb")
    content=f.read()
    f.close()
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    content=decryptor.update(content) + decryptor.finalize()
    f=open(os.path.join(path+"/temp/Segments","0.txt"),"wb")
    f.write(content)
    f.close()
    
def DBlowFish(path,key,iv):
    f=open(os.path.join(path+"/Segments","1.txt"),"rb")
    content=f.read()
    f.close()
    backend = default_backend()
    cipher = Cipher(algorithms.Blowfish(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    content=decryptor.update(content) + decryptor.finalize()
    f=open(os.path.join(path+"/temp/Segments","1.txt"),"wb")
    f.write(content)
    f.close()

def DTrippleDES(path,key,iv):
    f=open(os.path.join(path+"/Segments","2.txt"),"rb")
    content=f.read()
    f.close()
    backend = default_backend()
    cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    content=decryptor.update(content) + decryptor.finalize()
    f=open(os.path.join(path+"/temp/Segments","2.txt"),"wb")
    f.write(content)
    f.close()
    
def DIDEA(path,key,iv):
    f=open(os.path.join(path+"/Segments","3.txt"),"rb")
    content=f.read()
    f.close()
    backend = default_backend()
    cipher = Cipher(algorithms.IDEA(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    content=decryptor.update(content) + decryptor.finalize()
    # open(os.path.join(path+"/Segments","3.txt"),"wb").close()
    f=open(os.path.join(path+"/temp/Segments","3.txt"),"wb")
    f.write(content)
    f.close()
    
def DFernet(path,key):
	f=open(os.path.join(path+"/Segments","4.txt"),"rb")
	content=f.read()
	f.close()
	fer = Fernet(key)
	content=fer.decrypt(content)
	# open(os.path.join(path+"/Segments","4.txt"),"w").close()
	f=open(os.path.join(path+"/temp/Segments","4.txt"),"wb")
	f.write(content)
	f.close()

def HybridDeCryptKeys(key,path,filename):
    # f=open('Original.txt','rb')
    # key=f.read()
    # f.close()
    fer = Fernet(key)
    listDir=os.listdir(os.path.join(path,"Infos"))
    for i in listDir:
        path_=os.path.join(path+"/Infos",i)
        print(path_)
        k=open(path_,"rb")
        content=k.read()
        print(content)
        k.close()
        content=fer.decrypt(content)
        # open(os.path.join(path_+"/Infos",i),"wb").close()
        f=open(os.path.join(path+"/temp/Infos",i),"wb")
        print(i)
        f.write(content)
        f.close()
