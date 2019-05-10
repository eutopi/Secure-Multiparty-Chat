import sys, getopt
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from base64 import b64encode
from Crypto.Util import Counter
from Crypto.Signature import PKCS1_PSS

sndstatefile = 'sndstate.txt'
groupkeyfile = 'groupkey.txt'
# sndstatefile = ''
# groupkeyfile = ''
senderName = ''
outputfile = 'output.txt'

try:
    opts, args = getopt.getopt(sys.argv[1:],'hi:o:')
except getopt.GetoptError:
    print("Error Usage: reg_msg-gen.py -g <groupkeyfile> -s <sndstatefile> -m <sender ID>")
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print("Usage: reg_msg-gen.py -g <groupkeyfile> -s <sndstatefile> -m <sender ID>")
        sys.exit()
    elif opt == '-g':
        groupkeyfile = arg
    elif opt == '-s':
        sndstatefile = arg
    elif opt == '-m':
        senderName = arg

if len(groupkeyfile) == 0:
    print("Error: Name of groupkey file is missing.")
    sys.exit(2)

# read the content of the group key file
ifile = open(groupkeyfile, 'rt')
groupkey = ifile.readline()
ifile.close()

print(groupkey)
if len(groupkey) != 16:
    print('Error: Key string must be 16 character long.')
    sys.exit(2)

# read the sender and their rcvstate from the table file
# for A now
ifile = open('setup/table.txt', 'r')
line = ifile.read()
# line = ifile.readline() after making making new lines for table?
sender = line[len("member:"):len("member:")+1]
print(sender)
sndsqn = line[len("member:")+2:len("member:")+3]
sndsqn = int(sndsqn, base=10)
print(sndsqn)
ifile.close()

# read the message input
payload = input("Type the message: ")
print(payload)

"""
# RSA PKCS1 PSS SIGNATURE
# import the private key of inviter
sigkfile = open('setup/A-key.pem', 'r')
sigkeystr = sigkfile.read()
sigkfile.close()
sigkey = RSA.import_key(sigkeystr)
signer = PKCS1_PSS.new(sigkey)

NET_PATH = './netsim/network/'
OWN_ADDR = INVITER_ID
# ISO 11770-3/2
netif = network_interface(NET_PATH, OWN_ADDR)
print('Main loop started...')
"""

# compute payload_length + sig_length
payload_length = len(payload)
sig_length = 32  # SHA256 hash value is 32 bytes long

# compute message length...
# header: 7 bytes
#    sender: 1 byte
#    length: 2 btyes
#    sqn:    4 bytes
# nonce: AES.block_size
# payload: payload_length
# signature: sig_length 
msg_length = 7 + AES.block_size + payload_length + sig_length

# create header
header_sender = sender.encode('utf-8')   # message sender
header_length = msg_length.to_bytes(2, byteorder='big') # message length (encoded on 2 bytes)
header_sqn = (sndsqn + 1).to_bytes(4, byteorder='big')  # next message sequence number (encoded on 4 bytes)
header = header_sender + header_length + header_sqn 

nonce = Random.get_random_bytes(AES.block_size)

# create a counter object and set the nonce as its prefix and set the initial counter value to 0 
ctr = Counter.new(64, prefix=nonce, initial_value=0)

# create an AES-CTR cipher object and encrypt the header + payload
ENC = AES.new(groupkey, AES.MODE_CTR, counter=ctr)
encrypted = ENC.encrypt(header + payload)

print('Nonce: ' + nonce.hex())
print('Encrypted: ')
print(encrypted.hex())

# create a SHA256 hash object and hash the encrypted content
h = SHA256.new()
h.update(encrypted)

# sign the hash
signature = signer.sign(h)

#print(signature) 
print(signature.hex())

# save output sndstate of each sender
state = "enckey: " + enckey.hex() + '\n'
state = state + "groupkey: " + groupkey.hex() + '\n'
state = state + "sndsqn: " + str(sndsqn + 1)
state = state + "sender: " + str(sender)
ofile = open(sndstatefile, 'wb')
ofile.write(state)
ofile.close()

# write full encrypted message and signature 
ofile = open(outputfile, 'wb')
ofile.write(header + nonce + encrypted + signature)
ofile.close()
