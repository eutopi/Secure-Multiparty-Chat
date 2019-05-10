import sys, getopt
from Crypto.Hash import MD5
from Crypto.Util.strxor import strxor
from Crypto import Random
from Crypto.Cipher import AES

def generate():
    statefile = "prng/prngstate.txt"
    prnginput = Random.get_random_bytes(AES.block_size)

    # read the content of the state file
    ifile = open(statefile, 'r')
    line = ifile.readline()
    prngstate = bytes.fromhex(line[len("prngstate: "):len("prngstate: ")+32])
    ifile.close()

    # compute output and next state
    H = MD5.new()
    H.update(strxor(prnginput, prngstate))
    prngoutput = H.digest()
    prngstate = strxor(prngstate, prngoutput)

    # save state
    ofile = open(statefile, 'w')
    ofile.write("prngstate: " + prngstate.hex())
    ofile.close()

    #print output
    return prngoutput
