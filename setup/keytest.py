from Crypto.PublicKey import RSA

kfile = open("A-key.pem",'r')
privateks=kfile.read()
kfile.close()
privatek = RSA.import_key(privateks,passphrase = "a")
print(privatek.exportKey(format='PEM').decode('ASCII'))