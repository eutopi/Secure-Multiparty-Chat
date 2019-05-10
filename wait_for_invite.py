#!/usr/bin/env python3
#wait_for_invite.py

import os, sys, getopt
from netsim.netinterface import network_interface
from Crypto.Signature import PKCS1_PSS
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from datetime import datetime

'''
    Time = 17 bytes
    Cipher = 128 bytes (content = 1 byte (ID) and 16 bytes (public key))
    Signature = length varies, index at i=154 until the end
'''

#INVITER_ID = 'A'
#OWN_ADDR = 'B'
NET_PATH = './netsim/network/'

try:
    opts, args = getopt.getopt(sys.argv[1:], shortopts='hi:s:', longopts=['help', 'inviter=', 'self='])
except getopt.GetoptError:
    print('Usage: python wait_for_invite.py -i <inviter address> -s <self address>')
    sys.exit(1)

#if len(opts) == 0:
#     print('Usage: python network.py -p <network path> -a <address space> [--clean]')
#     sys.exit(1)

for opt, arg in opts:
    if opt == '-h' or opt == '--help':
        print('Usage: python wait_for_invite.py -i <inviter address> -s <self address>')
        sys.exit(0)
    elif opt == '-i' or opt == '--inviter':
        INVITER_ID = arg
    elif opt == '-s' or opt == '--self':
        OWN_ADDR = arg

def saveGroupKey(key, ADDR):
    '''
    f = open('MessageFormat/sndstate.txt', 'r')
    lines = f.readlines()
    lines[0] = 'groupkey: ' + key + '\n'
    print(lines)
    f.close()
    f = open('MessageFormat/sndstate1.txt', 'w')
    for l in lines:
        f.write(l)
    f.close()
    '''
    f = open('groupkey.txt', 'w')
    f.write(key)
    f.close()

# RSA PKCS1 PSS SIGNATURE
# import the public key of INVITER_ID
pubkeystr = ''
with open('setup/table.txt') as f:
    kfile = f.read()
pubkeys = kfile.split("member:")
pubkeys.pop(0)
for k in pubkeys:
    if k[0] == INVITER_ID:
        pubkeystr = k.split("key:")[1]
if(pubkeystr == ''):
    print('No public key string read!')

# import private key of invitee(self) for RSA
filename = 'setup/' + OWN_ADDR + '-key.pem'
prikfile = open(filename, 'r')
prikeystr = prikfile.read()
prikfile.close()

netif = network_interface(NET_PATH, OWN_ADDR)
print('Main loop started...')
while True:
    status, msg = netif.receive_msg(blocking=True)
    timestamp = msg[:17]
    ciphertext = msg[17:145]
    signature = msg[145:]
    print('Verifying time stamp...')
    current_time = datetime.now()
    current_timestamp = datetime.timestamp(current_time)
    print("Current timestamp: " + str(current_timestamp))
    print("Received timestamp: " + timestamp.decode('utf-8'))
    if (current_timestamp - float(timestamp) <= 3): # verify time stamp
        print('Time stamp verified')
        print('Verifying signature...')
        msg_to_be_signed = OWN_ADDR.encode('utf-8') + timestamp + ciphertext
        h = SHA256.new()
        h.update(msg_to_be_signed)
        pubkey = RSA.import_key(pubkeystr)
        verifier = PKCS1_PSS.new(pubkey)
        if verifier.verify(h, signature):
            print('Signature verified.')
            print('Decryption started...')
            prikey = RSA.import_key(prikeystr)
            cipher = PKCS1_OAEP.new(prikey)
            plaintext = (cipher.decrypt(ciphertext)).decode('utf-8')
            if str(plaintext)[0] == INVITER_ID:
                print('Decryption success.')
                print('Group ID is ' + plaintext[1])
                print('Group key is ' + plaintext[2:])
                #saveGroupKey(plaintext[2:], OWN_ADDR)
                break
            else:
                print('Failed.')
        else:
            print('Signature is incorrect! Message was either modified or this is someone else\'s invitation.')
    else:
        print('The timestamp has expired.')

