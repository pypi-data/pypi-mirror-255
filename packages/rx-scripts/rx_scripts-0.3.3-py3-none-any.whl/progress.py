from time import sleep
import sys

#-------------------------------------
def progress(n):
    global l_tick
    global counter
    prog=float(counter)/n
    counter+=1
    try:
        if prog < l_tick[0]:
            return
    except:
        print("Counter needs to be reset")
        exit(1)

    l_tick=l_tick[1:]
    val=int(20 * prog)

    sys.stdout.write('\r')
    sys.stdout.write("[%-20s] %d%%" % ('='*val, 5*val))
    sys.stdout.flush()
    sleep(0.25)
    if val == 20:
        sys.stdout.write("\n")
#-------------------------------------
def reset():
    global counter
    global l_tick
    counter=1

    for val in range(0, 105, 5):
        l_tick.append(val/100.)
#-------------------------------------
l_tick=[]
for val in range(0, 105, 5):
    l_tick.append(val/100.)
    
counter=1
