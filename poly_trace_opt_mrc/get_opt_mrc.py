import os
import sys


ITEM_PER_KB = 16   # every item is 64B so ITEM_PER_KB is 1024B/64B=16
MEM_UNIT = int(sys.argv[3]) * 1   # set 1KB as one memory unit

MAX_TRACE_LEN = 8000000

trace_name = sys.argv[1]
mrc = []

def get_mrc():
    global mrc
    opt_dis = []
    opt_dis_file = open("./" + trace_name + ".tr_forward-OPT-dis.txt")
    for line in opt_dis_file.readlines():
        dis = line.split()[2]
        if "INF" in dis:
            opt_dis += [MAX_TRACE_LEN]
        else:
            opt_dis += [int(dis)]
    opt_dis_file.close()
    
    for i in range(1, int(sys.argv[2])):
        mem = i * MEM_UNIT * ITEM_PER_KB
        miss = 0
        for dis in opt_dis:
            if dis > mem:
                miss += 1
        mrc += [float(miss) / float(len(opt_dis))]

    write_mrc()


def write_mrc():
    if not os.path.exists("mrcs"):
        os.makedirs("mrcs")
    
    print(trace_name)
    #mrc_file = open("mrcs/" + "opt_" + trace_name.split("/")[0] + "_" + trace_name.split("/")[1] + "_mrc", "w")
    mrc_file = open("mrcs/" + "opt_" + trace_name + "_mrc", "w")
    mrc_file.write("memory miss_ratio\n")
    for i in range(0, len(mrc)):
        mrc_file.write(str((i + 1) * MEM_UNIT) + " " + str(mrc[i]) + "\n")
    mrc_file.close()

get_mrc()
