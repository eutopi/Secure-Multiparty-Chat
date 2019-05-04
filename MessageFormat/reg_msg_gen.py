import sys, getopt
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from base64 import b64encode
from Crypto.Signature import PKCS1_PSS

statefile = "sndstate.txt"
inputfile = ""
outputfile = ""

try:
    opts, args = getopt.getopt(sys.argv[1:],'hi:o:')
except getopt.GetoptError:
    print("Usage: msg-gen.py -i <inputfile> -o <outputfile>")
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print("Usage: msg-gen.py -i <inputfile> -o <outputfile>")
        sys.exit()
    elif opt == '-i':
        inputfile = arg
    elif opt == '-o':
        outputfile = arg

if len(inputfile) == 0:
    print("Error: Name of input file is missing.")
    sys.exit(2)

if len(outputfile) == 0:
    print("Error: Name of output file is missing.")
    sys.exit(2)

# read the content of the state file
ifile = open(statefile, 'rt')
line = ifile.readline()
enckey = line[len("enckey: "):len("enckey: ")+32]
enckey = bytes.fromhex(enckey)
line = ifile.readline()
groupkey = line[len("groupkey: "):len("groupkey: ")+32]
groupkey = bytes.fromhex(groupkey)
line = ifile.readline()
sndsqn = line[len("sndsqn: "):len("sndsqn: ")+4]
sndsqn = int(sndsqn, base=10)
sender = line[len("sender: "):]
sender = int(sender, base=10)
ifile.close()

# read the content of the input file into variable payload
ifile = open(inputfile, 'rb')
payload = ifile.read()
ifile.close()

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
header_sender = sender.to_bytes(2, byteorder='big')   # message type 1
header_length = msg_length.to_bytes(2, byteorder='big') # message length (encoded on 2 bytes)
header_sqn = (sndsqn + 1).to_bytes(4, byteorder='big')  # next message sequence number (encoded on 4 bytes)
header = header_sender + header_length + header_sqn 

# encrypt what needs to be encrypted (header + payload)
nonce = Random.get_random_bytes(AES.block_size)
ENC = AES.new(enckey, AES.MODE_CBC, nonce)
encrypted = ENC.encrypt(header + payload)

# create a SHA256 hash object and hash the encrypted content
h = SHA256.new()
h.update(encrypted)

# sign the hash
signature = signer.sign(h)

#print(signature) 
print(signature.hex())

# write full encrypted message and signature 
ofile = open(outputfile, 'wb')
ofile.write(header + nonce + encrypted + signature)
ofile.close()

# save state
state = "enckey: " + enckey.hex() + '\n'
state = state + "groupkey: " + groupkey.hex() + '\n'
state = state + "sndsqn: " + str(sndsqn + 1)
state = state + "sender: " + str(sender)
ofile = open(statefile, 'wt')
ofile.write(state)
ofile.close()
