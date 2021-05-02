from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import os
def AES(path,key,iv):
    f=open(os.path.join(path+"/Segments","0.txt"),"r")
    content=f.read()
    f.close()
    content=content.encode()
    b=len(content)
    if(b%16!=0):
        while(b%16!=0):
            content+=" ".encode()
            b=len(content)
    backend = default_backend()  #cryptography was designed to support multiple cryptographic backends, but consumers rarely need this flexibility. Starting with version 3.1 backend arguments are optional and the default backend will automatically be selected if none is specified.
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)       #Cipher objects combine an algorithm such as AES with a mode like CBC. 
    encryptor = cipher.encryptor()              
    cont = encryptor.update(content) + encryptor.finalize() #Once finalize is called this object can no longer be used and update() and finalize() will raise an AlreadyFinalized exception.
    open(os.path.join(path+"/Segments","0.txt"),"wb").close()
    f=open(os.path.join(path+"/Segments","0.txt"),"wb")
    f.write(cont)
    f.close();

def BlowFish(path,key,iv):
    f=open(os.path.join(path+"/Segments","1.txt"),"r")
    content=f.read()
    f.close()
    content=content.encode()
    b=len(content)
    if(b%8!=0):
        while(b%8!=0):
            content+=" ".encode()
            b=len(content)
    backend = default_backend()
    cipher = Cipher(algorithms.Blowfish(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    cont = encryptor.update(content) + encryptor.finalize()
    open(os.path.join(path+"/Segments","1.txt"),"w").close()
    f=open(os.path.join(path+"/Segments","1.txt"),"wb")
    f.write(cont);
    f.close();


def TrippleDES(path,key,iv):
    f=open(os.path.join(path+"/Segments","2.txt"),"r");
    content=f.read();
    f.close();
    content=content.encode()
    b=len(content);
    if(b%8!=0):
        while(b%8!=0):
            content+=" ".encode()
            b=len(content);
    backend = default_backend();
    cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=backend);
    encryptor = cipher.encryptor();
    cont = encryptor.update(content) + encryptor.finalize();
    open(os.path.join(path+"/Segments","2.txt"),"w").close();
    f=open(os.path.join(path+"/Segments","2.txt"),"wb");
    f.write(cont);
    f.close();

def IDEA(path,key,iv):
	f=open(os.path.join(path+"/Segments","3.txt"),"r")
	content=f.read()
	f.close()
	content=content.encode()
	b=len(content)
	if(b%8!=0):
		while(b%8!=0):
			content+=" ".encode()
			b=len(content)
	backend = default_backend()
	cipher = Cipher(algorithms.IDEA(key), modes.CBC(iv), backend=backend)
	encryptor = cipher.encryptor()
	cont = encryptor.update(content) + encryptor.finalize()
	open(os.path.join(path+"/Segments","3.txt"),"w").close()
	f=open(os.path.join(path+"/Segments","3.txt"),"wb")
	f.write(cont)
	f.close()

def EFernet(path,key):
    f=open(os.path.join(path+"/Segments","4.txt"),"r")
    content=f.read()
    f.close()
    content=content.encode()
    fer = Fernet(key)
    content=fer.encrypt(content)
    open(os.path.join(path+"/Segments","4.txt"),'w').close()
    f=open(os.path.join(path+"/Segments","4.txt"),"wb")
    f.write(content)
    f.close()

def HybridCryptKeys(path):
    key = Fernet.generate_key()
    f=open('Original.txt','wb')
    f.write(key)
    f.close()
    listDir=os.listdir(path+"/Infos")
    fer = Fernet(key)
    for i in listDir:
        KI=open(path+'/Infos/'+i,'rb')
        content=KI.read()
        KI.close()
        content=fer.encrypt(content)
        open(os.path.join(path+"/Infos",i),'wb').close()
        f=open(os.path.join(path+"/Infos",i),"wb")
        f.write(content)
        f.close()
    return key

