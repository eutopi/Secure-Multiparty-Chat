import os, sys, getopt
from invite import invite
from wait_for_invite import receive_invite
from reset_rcvsqn_table import reset_rcv_sqn

OWN_ADDR = ''
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
    INVITEE_LIST = input("Please enter who you are inviting:")
    GROUP_ID = input("Please enter group id:")
    groupkey = invite(OWN_ADDR, INVITEE_LIST, GROUP_ID)
else:
    INVITER = input("Please enter who you are receiving the invitation from: ")
    GROUP_ID = input("Please enter group id: ")
    groupkey = receive_invite(OWN_ADDR, INVITER, GROUP_ID)

print("Key exchange complete")
reset_rcv_sqn(OWN_ADDR)
while True:
    status, msg = netif.receive_msg(blocking=False)
    if status:
        print(msg)
    else:
        msg = OWN_ADDR + input("Enter new message: ")
