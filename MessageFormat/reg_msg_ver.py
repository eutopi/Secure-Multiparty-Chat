import sys, getopt
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from base64 import b64encode
from Crypto.Signature import PKCS1_PSS

statefile = "rcvstate.txt"
inputfile = ""
outputfile = ""

try:
    opts, args = getopt.getopt(sys.argv[1:],'hi:o:')
except getopt.GetoptError:
    print("Usage: msg-ver.py -i <inputfile> -o <outputfile>")
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print("Usage: msg-ver.py -i <inputfile> -o <outputfile>")
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

# read the content of the input file into msg
ifile = open(inputfile, 'rb')
msg = ifile.read()
ifile.close()

# parse the message
header_length = 7                 # header is 7 bytes long
header = msg[0:header_length]
nonce = msg[header_length:header_length+AES.block_size]   # iv is AES.block_size bytes long
sig_length = 32                     # SHA256 hash is 32 bytes long
encrypted = msg[AES.block_size+header_length:-sig_length]  # the encrypted part is the header and Payload
sig = msg[-sig_length:]
header_sender = header[0:1]         # sender is encoded on 1 byte 
header_length = header[1:3]         # msg length is encoded on 2 bytes 
header_sqn = header[3:7]            # msg sqn is encoded on 4 bytes

print("Message header:")
print("   - header_sender: " + header_sender.hex() 
print("   - message length: " + header_length.hex() + " (" + str(int.from_bytes(header_length, byteorder='big')) + ")")
print("   - message sequence number: " + header_sqn.hex() + " (" + str(int.from_bytes(header_sqn, byteorder='big')) + ")")

# check the msg length
if len(msg) != int.from_bytes(header_length, byteorder='big'):
    print("Warning: Message length value in header is wrong!")
    print("Processing is continued nevertheless...")

# check the sequence number
print("Expecting sequence number " + str(rcvsqn + 1) + " or larger...")
sndsqn = int.from_bytes(header_sqn, byteorder='big')
if (sndsqn <= rcvsqn):
    print("Error: Message sequence number is too old!")
    print("Processing completed.")
    sys.exit(1)    
print("Sequence number verification is successful.")

# decrypt the encrypted part
print("Decryption is attempted...")
ENC = AES.new(enckey, AES.MODE_CBC, nonce)  # create AES cipher object
decrypted = ENC.decrypt(encrypted)       # decrypt the encrypted part of the message

# parse decrypted into payload
msg_signed = decrypted

# create a SHA256 hash object and hash the content of the input file
h = SHA256.new()
h.update(msg_signed)

# read the signature from the signature file and convert to binary from base64
sfile = open(signaturefile, 'rb')
sfile.readline() # reading the line '--- RSA PKCS1 PSS SIGNATURE ---'
signature = b64decode(sfile.readline())
sfile.close()

# verify the signature
verifier = PKCS1_PSS.new(groupkey)
result = verifier.verify(h, signature)

# print the result of the verification on the screen 
print('Done.')
if result:
        print('The signature is correct.')
else:
        print('The signature is incorrect.')

# write payload out
ofile = open(outputfile, 'wb')
ofile.write(payload)
ofile.close()
print("Payload is saved to " + outputfile)

# save state
state = "enckey: " + enckey.hex() + '\n'
state = state + "groupkey: " + groupkey.hex() + '\n'
state = state + "sndsqn: " + str(sndsqn + 1)
state = state + "sender: " + str(sender)
ofile = open(statefile, 'wt')
ofile.write(state)
ofile.close()
print("Receiving state is saved.")
print("Processing completed.")
