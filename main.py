import os, sys, getopt
from netsim.netinterface import network_interface
import select
from invite import invite
from wait_for_invite import receive_invite
from reset_sqn_table import reset_sqn
from reg_msg_ver import receive
from reg_msg_gen import send

OWN_ADDR = ''
NET_PATH = './netsim/network/'
invite_flag = False

try:
    opts, args = getopt.getopt(sys.argv[1:], shortopts='hs:i', longopts=['help', 'self=', 'invite'])
except getopt.GetoptError:
    print('Usage: python main.py -s <self address> -i <invite: include for true, else false>')
    sys.exit(1)

if len(opts) == 0:
    print('Usage: python main.py -s <self address> -i <invite: include for true, else false>')
    sys.exit(1)

for opt, arg in opts:
    if opt == '-h' or opt == '--help':
        print('Usage: python main.py -s <self address> -i <invite: include for true, else false>')
        sys.exit(0)
    elif opt == '-s' or opt == '--self':
        OWN_ADDR = arg
    elif opt == '-i' or opt == '--invite':
        invite_flag = True

netif = network_interface(NET_PATH, OWN_ADDR)
if invite_flag:
    password = input("Please enter your password: ")
    INVITEE_LIST = input("Please enter who you are inviting: ")
    GROUP_ID = input("Please enter group id: ")
    print("")
    groupkey = invite(netif, OWN_ADDR, INVITEE_LIST, GROUP_ID, password)
else:
    password = input("Please enter your password: ")
    INVITER = input("Please enter who you are receiving the invitation from: ")
    GROUP_ID = input("Please enter group id: ")
    groupkey = receive_invite(netif, OWN_ADDR, INVITER, GROUP_ID, password)

print("Key exchange complete")
print("")
reset_sqn(OWN_ADDR)
print("")

sys.stdout.write("Begin chatting!\n\n")
sys.stdout.flush()
while True:
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    if ready:
        m = sys.stdin.readline().rstrip('\n')
        snd_msg = OWN_ADDR + ": " + m
        to_send = send(OWN_ADDR, snd_msg, groupkey, password)
        netif.send_msg('S', to_send)
    else:
        status, rcv_msg = netif.receive_msg(blocking=False)
        if status:
            plaintext = receive(OWN_ADDR, rcv_msg, groupkey)
            if plaintext != None:
                print(plaintext)
'''
while True:
    status, rcv_msg = netif.receive_msg(blocking=False)
    if status:
        plaintext = receive(OWN_ADDR, rcv_msg, groupkey)
        print("\n" + plaintext + "\n")
    else:
        snd_msg = OWN_ADDR + ": " + input("Enter new message: ")
        to_send = send(OWN_ADDR, snd_msg, groupkey, password)
        netif.send_msg('S', to_send)
'''
