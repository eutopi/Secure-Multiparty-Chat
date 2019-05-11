import sys, getopt
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import base64
from Crypto.Util import Counter
from Crypto.Signature import PKCS1_PSS

encfile = ''
groupkeyfile = 'groupkey.txt'
statefile = 'rcvstate.txt'
senderID = 'A'

try:
    opts, args = getopt.getopt(sys.argv[1:],'hi:o:')
except getopt.GetoptError:
    print("Usage: msg-ver.py -m <sender ID>")
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print("Usage: msg-ver.py -m <sender ID>")
        sys.exit()
    elif opt == '-i':
        senderID = arg

# read the content of the encrypted file into msg
encfile = 'output' + senderID + '.txt'
ifile = open(encfile, 'rb')
msg = ifile.read()
ifile.close()

# read the content of the group key file
ifile = open(groupkeyfile, 'rb')
groupkey = ifile.read()
ifile.close()

#CONVERT MSG FORMAT INTO STH ELSE?
# msg = msg.decode??



# parse the message
header_length = 7                 # header is 7 bytes long
header = msg[0:header_length]
nonce = msg[header_length:header_length+8]   # nonce is 8 bytes long
sig_length = 32                     # SHA256 hash is 32 bytes long
encrypted = msg[header_length+8:-sig_length]  # the encrypted part is the header and Payload
sig = msg[-sig_length:]
header_sender = header[0:1]         # sender is encoded on 1 byte 
header_length = header[1:3]         # msg length is encoded on 2 bytes 
header_sqn = header[3:7]            # msg sqn is encoded on 4 bytes

print("Message header:")
print("   - header_sender: " + header_sender.hex())
print("   - message length: " + header_length.hex() + " (" + str(int.from_bytes(header_length, byteorder='big')) + ")")
print("   - message snd sequence number: " + header_sqn.hex() + " (" + str(int.from_bytes(header_sqn, byteorder='big')) + ")")

# check the msg length
if len(msg) != int.from_bytes(header_length, byteorder='big'):
    print("Warning: Message length value in header is wrong!")
    print("Processing is continued nevertheless...")

# read the rcvstate
rcvstatefile = 'rcvstate' + senderID + '.txt'
ifile = open(rcvstatefile, 'r')
rcvsqn = ifile.read()
ifile.close()
rcvsqn = rcvsqn[len("rcvsqn: "):len("rcvsqn: ")+1]
rcvsqn = int(rcvsqn)

# check the sequence number
print("Expecting sequence number " + str(rcvsqn+1) + " or larger...")
sndsqn = int.from_bytes(header_sqn, byteorder='big')
if (sndsqn <= rcvsqn):
    print("Error: Message sequence number is too old!")
    print("Processing completed.")
    sys.exit(1)    
print("Sequence number verification is successful.")

# decrypt the encrypted part
print("Decryption is attempted...")
ctr = Counter.new(64, prefix=nonce, initial_value=0)

# create an AES-CTR cipher object
groupkey = groupkey
ENC = AES.new(groupkey, AES.MODE_CTR, counter=ctr)

# decrypt the header + payload
msg_signed = ENC.decrypt(encrypted)

# create a SHA256 hash object and hash the content of the input file
h = SHA256.new()
h.update(msg_signed)

# import the pubkey of each users from the table
# **After update**
# fileName = 'setup/table' + senderID + '.txt'
# tablefile = open(fileName, 'r')
# content = tablefile.read()
# tablefile.close()

# for A now
ifile = open('setup/table_temp.txt', 'r')
content = ifile.read()
ifile.close()

#index of the pubkey
pubkeyIndex = content.find(str(senderID) + "|") + 9
pubkey = content[pubkeyIndex:pubkeyIndex+219]
print('pubkey of the sender:')
print(pubkey)
#pubkey to byte

pubkey = base64.b64decode(pubkey) #ERROR
#AttributeError: 'bytes' object has no attribute 'n'
#Trying to convert pubkey into bytes and verify signature



# verify the signature
verifier = PKCS1_PSS.new(pubkey) #pubkey of each users from the table
result = verifier.verify(h, sig)

# print the result of the verification on the screen 
print('Done.')
if result:
    print('The signature is correct.')
    print('This is your message:')
    print(payload)

    # update rcvsqn
    state = "rcvsqn: " + str(rcvsqn + 1)
    rcvstatefile = 'rcvstate' + senderID + '.txt'
    ofile = open(rcvstatefile, 'wt')
    ofile.write(state)
    ofile.close()
    print("Receiving state is saved.")
    print("Processing completed.")

else:
    print('The signature is incorrect.')

