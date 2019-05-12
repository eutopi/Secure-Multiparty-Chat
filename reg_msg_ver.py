import sys, getopt
from netsim.netinterface import network_interface
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import base64
from Crypto.Util import Counter
from Crypto.Signature import PKCS1_PSS
from Crypto.PublicKey import RSA
'''
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

NET_PATH = './netsim/network/'
OWN_ADDR = senderID
netif = network_interface(NET_PATH, OWN_ADDR)
# read the message
status, msg = netif.receive_msg(blocking=True)

# read the content of the group key file
ifile = open(groupkeyfile, 'rb')
groupkey = ifile.read()
ifile.close()
'''
def receive(OWN_ADDR, msg, groupkey):

    # parse the message
    header_length = 8                 # header is 8 bytes long
    header = msg[0:header_length]
    nonce = msg[header_length:header_length+8]   # nonce is 8 bytes long
    sig_length = 128
    encrypted = msg[header_length+8:-sig_length]
    sig = msg[-sig_length:]
    header_sender = header[0:1]         # sender is encoded on 1 byte
    header_length = header[1:4]         # msg length is encoded on 2 bytes
    header_sqn = header[4:8]            # msg sqn is encoded on 4 bytes

    #print("Message header:")
    #print("   - header_sender: " + header_sender.decode('utf-8'))
    #print("   - message length: " + header_length.decode('utf-8'))
    #print("   - message snd sequence number: " + header_sqn.hex() + " (" + str(int.from_bytes(header_sqn, byteorder='big')) + ")")
    senderID = header_sender.decode('utf-8')

    # check the msg length
    if str(len(msg)) != header_length.decode('utf-8'):
        print("Warning: Message length value in header is wrong!")
        print("Processing is continued nevertheless...")

    # read the rcvstate
    tablefile = open('setup/table%s.txt'%OWN_ADDR, 'r')
    table = tablefile.read()
    tablefile.close()
    rcvIndex = table.find(senderID + '|')+2
    rcvsqn = table[rcvIndex]
    rcvsqn = int(rcvsqn)

    # check the sequence number
    #print("Expecting sequence number " + str(rcvsqn+1) + " or larger...")
    sndsqn = int.from_bytes(header_sqn, byteorder='big')
    if (sndsqn <= rcvsqn):
        print("Error: Message sequence number is too old!")
        print("Processing completed.")
        sys.exit(1)
    #print("Sequence number verification is successful.")

    # decrypt the encrypted part
    #print("Decryption is attempted...")
    ctr = Counter.new(64, prefix=nonce, initial_value=0)

    # create an AES-CTR cipher object
    ENC = AES.new(groupkey, AES.MODE_CTR, counter=ctr)

    # decrypt the header + payload
    plaintext = ENC.decrypt(encrypted)

    # create a SHA256 hash object and hash the content of the input file
    h = SHA256.new()
    h.update(encrypted)

    # import the pubkey of each users from the table
    # **After update**
    # fileName = 'setup/table' + senderID + '.txt'
    # tablefile = open(fileName, 'r')
    # content = tablefile.read()
    # tablefile.close()
    '''
    # for A now
    # ifile = open('setup/table_temp.txt', 'r')
    # content = ifile.read()
    # ifile.close()

    #index of the pubkey
    # pubkeyIndex = content.find(str(senderID) + "|") + 9
    # pubkey = content[pubkeyIndex:pubkeyIndex+219]
    # print('pubkey of the sender:')
    # print(pubkey)
    '''

    # RSA PKCS1 PSS SIGNATURE
    # import the public key of INVITER_ID
    pubkeystr = ''
    with open('setup/table%s.txt'%OWN_ADDR) as f:
        kfile = f.read()
    pubkeys = kfile.split("member:")
    pubkeys.pop(0)
    for k in pubkeys:
        if k[0] == senderID:
            pubkeystr = k.split("key:")[1]
    if(pubkeystr == ''):
        print('No public key string read!')
        sys.exit(1)

    #print('pubkeystr:' + pubkeystr)
    pubkey = RSA.import_key(pubkeystr)

    # verify the signature
    verifier = PKCS1_PSS.new(pubkey) #pubkey of each users from the table
    result = verifier.verify(h, sig)

    #print('signature: '+str(sig))
    #print('signaturelength: ' + str(len(sig)))

    # print the result of the verification on the screen
    #print('Done.')
    if result:

        #update rcvsqn in the table file
        fileName = 'setup/table%s.txt'%OWN_ADDR
        tablefile = open(fileName, 'r')
        content = tablefile.read()
        rcvIndex = content.find(senderID + '|')+2
        #print('new rcvIndex' + content[rcvIndex:rcvIndex+1])
        content = content[:rcvIndex] + str(sndsqn) + content[rcvIndex+1:]
        tablefile.close()
        tablefile = open(fileName, 'w')
        tablefile.write(content)
        tablefile.close()
        #print("Receiving state is saved.")
        #print("Processing completed.")

        #print('The signature is correct.')
        #print('This is your message:')
        return plaintext.decode('utf-8')
    else:
        print('The signature is incorrect.')

