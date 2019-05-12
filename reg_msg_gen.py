import sys, getopt
from netsim.netinterface import network_interface
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from base64 import b64encode
from Crypto.Util import Counter
from Crypto.Signature import PKCS1_PSS
from Crypto.PublicKey import RSA

'''
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
'''
'''
# if snd state not exists, create one
try:
    sndstatefile = 'sndstate' + senderID + '.txt'
    file = open(sndstatefile, 'r')
    content = file.read()
    file.close()
    sndsqn = content[len("sndsqn: "):]
    print('sndsqn:' + sndsqn)
    sndsqn = int(sndsqn)
    # Store configuration file values
except FileNotFoundError:
    # Keep preset values
    state = "sndsqn: " + str(0)
    sndstatefile = 'sndstate' + senderID + '.txt'
    sndsqn = 0
    ofile = open(sndstatefile, 'wt')
    ofile.write(state)
    ofile.close()
    print("Created new sndstate file")

# for A now
ifile = open('setup/table.txt', 'r')
content = ifile.read()
ifile.close()

print('senderID:' + senderID)

# read the message input
payload = input("Type the message: ")
'''
def send(senderID, payload, groupkey, password):

    nonce = Random.get_random_bytes(8)
    # create a counter object and set the nonce as its prefix and set the initial counter value to 0
    ctr = Counter.new(64, prefix=nonce, initial_value=0)

    # create an AES-CTR cipher object and encrypt the header + payload
    ENC = AES.new(groupkey, AES.MODE_CTR, counter=ctr)
    payload = payload.encode('utf-8')
    encrypted = ENC.encrypt(payload)

    # create a SHA256 hash object and hash the encrypted content
    h = SHA256.new()
    h.update(encrypted)

    # RSA PKCS1 PSS SIGNATURE
    sigkfile = open("setup/%s-key.pem"%senderID,'r')
    sigkeystr = sigkfile.read()
    sigkfile.close()
    sigkey = RSA.import_key(sigkeystr,passphrase = password)
    signer = PKCS1_PSS.new(sigkey)

    # sign the hash
    signature = signer.sign(h)

    #update sndsqn in the sndstate file
    fileName = 'setup/sndstate' + senderID + '.txt'
    ofile = open(fileName, 'r')
    temp = ofile.readline()
    sndsqn = int(temp.split('sndsqn: ')[1])
    #print(sndsqn)
    ofile.close()
    ofile = open(fileName, 'w')
    ofile.write('sndsqn: ' + str(sndsqn+1))
    ofile.close()
    
    # compute payload_length + sig_length
    payload_length = len(encrypted)
    sig_length = 128
    
    # compute message length...
    # header:
    #    sender: 1 byte
    #    length: 3 btyes
    #    sqn:    4 bytes
    # nonce: 8 bytes
    # payload: payload_length
    # signature: sig_length
    msg_length = 8 + len(nonce) + payload_length + sig_length
    
    # create header
    header_sender = senderID.encode('utf-8')   # message sender
    header_length = str(msg_length).encode('utf-8') # message length (encoded on 3 bytes)
    header_sqn = (sndsqn + 1).to_bytes(4, byteorder='big')  # next message sequence number (encoded on 4 bytes)
    header = header_sender + header_length + header_sqn
    
    return (header + nonce + encrypted + signature)

    '''
    NET_PATH = './netsim/network/'
    OWN_ADDR = senderID
    netif = network_interface(NET_PATH, OWN_ADDR)
    print('Main loop started...')
    # send message to server
    netif.send_msg('S',header + nonce + encrypted + signature)
    '''


