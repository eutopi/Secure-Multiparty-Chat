import sys, getopt
from Crypto.Util import Counter

def reset_sqn(OWN_ADDR):
    #reset all the rcvsqn values in the table.txt
    fileName = 'setup/table%s.txt'%OWN_ADDR
    tablefile = open(fileName, 'r')
    content = tablefile.read()
    tablefile.close()

    tablefile = open(fileName, 'wt')
    rcvIndexA = content.find('A|')+2
    content = content[:rcvIndexA] + '0' + content[rcvIndexA+1:]
    rcvIndexB = content.find('B|')+2
    content = content[:rcvIndexB] + '0' + content[rcvIndexB+1:]
    rcvIndexC = content.find('C|')+2
    content = content[:rcvIndexC] + '0' + content[rcvIndexC+1:]
    tablefile.write(content)
    tablefile.close()

    print('Receive sequences reset to 0 successfully.')

    state = "sndsqn: " + str(0)
    sndstatefile = 'setup/sndstate' + OWN_ADDR + '.txt'
    ofile = open(sndstatefile, 'wt')
    ofile.write(state)
    ofile.close()
    print("Created new sndstate file.")

