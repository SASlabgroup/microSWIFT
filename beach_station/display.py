#!/usr/bin/env python3

import time
import subprocess
from multiprocessing import Process, Queue
import os

RADIOFILE='radio/radio.out'
POSFILE="anim/pos"

GPXSEECOMMAND=["/usr/bin/gpxsee", "anim/pos.buoy2", "anim/pos.buoy3", "anim/pos.buoy4", "anim/pos.buoy5", "anim/pos.buoy6", "anim/pos.buoy7", "anim/pos.buoy8", "anim/pos.buoy9", "anim/pos.buoy10", "anim/pos.buoy11", "anim/pos.buoy12"]

def run_gpxsee(queue):
    ret=""
    proc = subprocess.Popen(GPXSEECOMMAND)
    pid=proc.pid
    print("GPXSee has PID %s" % pid)
    while ret != "done":
        ret = queue.get()
        print("gpxsee - got %s !" % ret)
        if ret == "go":
            # os.system("WID=$(xdotool search --name  gpxsee | head -1); xdotool windowactivate $WID; xdotool key --window $WID F5")
            #             xdotool search --name gdb key ctrl+c
            # os.system("xdotool search --name  gpxsee key F5")
            os.system("xdotool search --all --pid %s --name gpxsee key F5" % pid)
            while not queue.empty():
                ret = queue.get()
                print("  emptying - got %s !" % ret)
            ret=""
        time.sleep(0.5)


def watch(filename, words):
    fp = open(filename, 'r')
    while True:
        new = fp.readline()
        # Once all lines are read this just returns ''
        # until the file changes and a new line appears

        if new:
            for word in words:
                if word in new:
                    yield (word, new)
        else:
            time.sleep(0.5)

fn = RADIOFILE
words = ['GPGGA']
lines =[]
lon=[]
lat=[]
first=True
proc=None
q = Queue()
p = Process(target=run_gpxsee, args=(q,))
p.start()

lines = dict()
lhead = dict()
lhead["buoy2"]="$GPWPL,replaceme,BUOY2,*66"
lhead["buoy3"]="$GPWPL,replaceme,BUOY3,*66"
lhead["buoy4"]="$GPWPL,replaceme,BUOY4,*66"
lhead["buoy5"]="$GPWPL,replaceme,BUOY5,*66"
lhead["buoy6"]="$GPWPL,replaceme,BUOY6,*66"
lhead["buoy7"]="$GPWPL,replaceme,BUOY7,*66"
lhead["buoy8"]="$GPWPL,replaceme,BUOY8,*66"
lhead["buoy9"]="$GPWPL,replaceme,BUOY9,*66"
lhead["buoy10"]="$GPWPL,replaceme,BUOY10,*66"
lhead["buoy11"]="$GPWPL,replaceme,BUOY11,*66"
lhead["buoy12"]="$GPWPL,replaceme,BUOY12,*66"
        
for hit_word, hit_sentence in watch(fn, words):
    print ("Found %r in line: %r" % (hit_word, hit_sentence))
    # line=hit_sentence[16:-4]
    line=hit_sentence.split(',')[2:-1]
    buoy=hit_sentence.split(',')[-1:]
    buoyname=buoy[0].split('\\')[0]
    print ("   buoyname %s" % buoyname)
    if not buoyname in lines.keys():
        lines[buoyname]=[]
        lhead[buoyname]="$GPWPL,replaceme," + buoyname + ",*66"
    lines[buoyname].append(','.join(line))
    if(len(lines[buoyname])>=15):
        lines[buoyname].pop(0)
    print ("   mod is %r %s" % (line, buoyname))
    print ("     list is %r" % lines[buoyname])
    with open(POSFILE + '.' + buoyname, "w") as f:
        header=lhead[buoyname]
        print ("going to remove %s with %s" % ("replaceme", ','.join(lines[buoyname][-1].split(',')[3:6])) )
        header = header.replace("replaceme", ','.join(lines[buoyname][-1].split(',')[2:6]))
        print ("going to write header %s" ,header)
        f.write(header + "\n")
        for l in lines[buoyname]:
            f.write(l + "\n")
    q.put('go')

p.join()
