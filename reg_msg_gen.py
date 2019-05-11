import sys, getopt
from netsim.netinterface import network_interface
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from base64 import b64encode
from Crypto.Util import Counter
from Crypto.Signature import PKCS1_PSS
from Crypto.PublicKey import RSA

sndstatefile = ''
groupkeyfile = 'groupkey.txt'
senderID = 'A'
outputfile = ''

try:
    opts, args = getopt.getopt(sys.argv[1:],'hi:o:')
except getopt.GetoptError:
    print("Error Usage: reg_msg-gen.py -m <sender ID>")
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print("Usage: reg_msg-gen.py -m <sender ID>")
        sys.exit()
    # elif opt == '-g':
    #     groupkeyfile = arg
    # elif opt == '-s':
    #     sndstatefile = arg
    elif opt == '-i':
        senderID = arg

if len(senderID) == 0:
    print("Error: Sender ID is missing.")
    sys.exit(2)

# read the content of the group key file
ifile = open(groupkeyfile, 'rb')
groupkey = ifile.readline()
ifile.close()

print(groupkey)
if len(groupkey) != 16:
    print('Error: Key string must be 16 character long.')
    sys.exit(2)

# read the sender and their rcvstate from the table file
# **After update**
# fileName = 'setup/table' + senderID + '.txt'
# tablefile = open(fileName, 'r')
# content = tablefile.read()
# tablefile.close()

# for A now
ifile = open('setup/table_temp.txt', 'r')
content = ifile.read()
ifile.close()

sndsqnIndex = content.find(str(senderID)) + 2
sndsqn = content[sndsqnIndex:sndsqnIndex+1]
sndsqn = int(sndsqn, base=10)
print('senderID:' + senderID)
print('sndsqn:' + str(sndsqn))

"""
#AFTER tableA/B/C format updated
fileName = 'setup/table' + senderID + '.txt'
tablefile = open(fileName, 'r')
content = file.read()
tablefile.close()
#index of the sendsequence num from tableX.txt
sndsqnIndex = content.find(str(senderID) + "|") + 1 
sndsqn = content[sndsqnIndex:sndsqnIndex+1]
print('sndsqn of the sender:' + sndsqn)
"""


# read the message input
payload = input("Type the message: ")
print(payload)

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
header_sender = senderID.encode('utf-8')   # message sender
header_length = str(msg_length).encode('utf-8') # message length (encoded on 2 bytes)
print(header_length)
header_sqn = (sndsqn + 1).to_bytes(4, byteorder='big')  # next message sequence number (encoded on 4 bytes)
header = header_sender + header_length + header_sqn 

nonce = Random.get_random_bytes(8)

# create a counter object and set the nonce as its prefix and set the initial counter value to 0 
ctr = Counter.new(64, prefix=nonce, initial_value=0)

# create an AES-CTR cipher object and encrypt the header + payload
groupkey = groupkey
ENC = AES.new(groupkey, AES.MODE_CTR, counter=ctr)
payload = payload.encode('utf-8')
encrypted = ENC.encrypt(payload)

print('Nonce: ' + nonce.hex())
print('Encrypted: ')
# print(encrypted)
print(encrypted.hex())

# create a SHA256 hash object and hash the encrypted content
h = SHA256.new()
h.update(encrypted)

# RSA PKCS1 PSS SIGNATURE
# import the private key of inviter
fileName = 'setup/' + senderID
fileName = fileName+ '-key.pem'
sigkfile = open(fileName, 'r')
sigkeystr = sigkfile.read()
sigkfile.close()
sigkey = RSA.import_key(sigkeystr)
signer = PKCS1_PSS.new(sigkey)

# sign the hash
signature = signer.sign(h)

NET_PATH = './netsim/network/'
OWN_ADDR = senderID
# ISO 11770-3/2
netif = network_interface(NET_PATH, OWN_ADDR)
print('Main loop started...')

#print(signature) 
print(signature.hex())

outputfile = 'output' + senderID
outputfile = outputfile + '.txt'

# write full encrypted message and signature 
ofile = open(outputfile, 'wb')
ofile.write(header + nonce + encrypted + signature)
ofile.close()


####UPDATE THE SNDSQN NUMBER IN THE TABLE ####
# save output sndsqn of each sender on the table
"""
snd_state = str(sndsqn + 1)

sndsqnIndex = content.find(str(senderID)) + 2
content = content[:sndsqnIndex] + snd_state + content[sndsqnIndex+1:]

# fileName = 'setup/table' + senderID + '.txt'
# tablefile = open(fileName, 'wt')
# ofile.write(content)
# tablefile.close()
"""


# if rcv state not exists, create one
try:
    rcvstatefile = 'rcvstate' + senderID + '.txt'
    ofile = open(rcvstatefile, 'r')
    # Store configuration file values
except FileNotFoundError:
    # Keep preset values
    state = "rcvsqn: " + str(0)
    rcvstatefile = 'rcvstate' + senderID + '.txt'
    ofile = open(rcvstatefile, 'wt')
    ofile.write(state)
    ofile.close()
    print("Created new rcvstate file")
