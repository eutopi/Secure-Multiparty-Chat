import select
import sys

def timeout_input(timeout, prompt="", timeout_value=None):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    while True:
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            print(sys.stdin.readline().rstrip('\n'))
        else:
            #sys.stdout.write('\n')
            #sys.stdout.flush()
            print(timeout_value)

timeout_input(3, "enter: ", "new message")
