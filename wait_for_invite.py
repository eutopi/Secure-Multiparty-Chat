#!/usr/bin/env python3
#wait_for_invite.py

from netinterface import network_interface
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

NET_PATH = './network/'
for opt, arg in opts:
    if opt == '-h' or opt == '--help':
        print('Usage: python wait_for_invite.py -a <network path>')
        sys.exit(0)
    elif opt == '-a' or opt == '--addr':
        OWN_ADDR = arg

kfile = open('rsa private key of invitee', 'r')
prikeystr = kfile.read()
kfile.close()
key = RSA.import_key(prikeystr)
cipher = PKCS1_OAEP.new(key)

netif = network_interface(NET_PATH, OWN_ADDR)
print('Main loop started...')
while True:
    status, msg = netif.receive_msg(blocking=True)
    dec_msg = cipher.decrypt(msg.decode('utf-8'))
    if (dec_msg[0:2] == 'A0'):
        groupid = dec_msg[1]
        groupkey = dec_msg[2:19]
        time = dec_msg[19:45]
        signature = dec_msg[45:]
        
        # Verify signature
        msg_signed = OWN_ADDR + groupid + groupkey + time
        h = SHA256.new()
        h.update(msg_signed)
        kfile = open('pem signature key of inviter', 'r')
        pubkeystr = kfile.read()
        kfile.close()
        pubkey = RSA.import_key(pubkeystr)
        verifier = PKCS1_PSS.new(pubkey)
        if verifier.verify(h, signature):
            # Check timestamp
            print("Successful, group key received is: " + groupkey)
            break
