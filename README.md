# Secure Multiparty Chat

## Handshake Protocol
On five separate terminals run in the following order:

```
1. netsim/network.py -a 'SABC' -c 
2. netsim/server.py
3. setup/setup.py -n 3 (-n means the total number of people in the group) (well... i think run it in one terminal is enough?)
4. wait_for_invite.py -i A -s B (-i means inviter is A, -s means self is B)
5. wait_for_invite.py -i A -s C (-i means inviter is A, -s means self is C)
6. invite.py (inviter A sends invitation to B and C)
```
