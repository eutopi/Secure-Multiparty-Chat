import sys, getopt
from Crypto.PublicKey import RSA
from base64 import b64encode

tablefile = "table.txt"
privatekfile = "privatek.txt"

totalnum = 3
otablefile = open(tablefile,'w')


#create key pairs for each memeber
member = 'A'
for i in range(totalnum):
	# create key pairs for each memeber
	key = RSA.generate(1024)
	publickey = key.publickey().exportKey(format='PEM').decode('ASCII')#.splitlines()[1:-1]
	#publickey = b''.join(publickey).decode('ASCII')

	privatekey = key.exportKey(format='PEM').decode('ASCII')#.splitlines()[1:-1]
	#privatekey = b''.join(privatekey).decode('ASCII')
	sqnr = 0
	# output private key pem file 
	pemfile = "%s-key.pem"%member
	opemfile = open(pemfile,'w')
	opemfile.write(key.exportKey(format='PEM').decode('ASCII'))
	opemfile.close()
	# output table file 
	otablefile.write('member:'+member+"|"+str(sqnr)+"|")
	otablefile.write('key:'+publickey)
	# output private key file 
	privatekfile = "privatek%s.txt"%member
	okeyfile = open(privatekfile,'w')
	okeyfile.write(privatekey)
	okeyfile.close()
	member=chr(ord(member)+1)

otablefile.close()
# create certificate for each member