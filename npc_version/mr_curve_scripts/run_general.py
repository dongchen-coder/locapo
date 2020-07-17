import argparse
import os
import subprocess
from subprocess import PIPE,STDOUT,check_output,Popen
import shlex
import time
import csv
import signal
VERBOSE = False
if __name__=="__main__":
    p=argparse.ArgumentParser(description="Run Code for a student")
    p.add_argument("command", help="command to run code")
    p.add_argument("path_to_input")
    p.add_argument("path_to_output")
    p.add_argument("output_name_append")
    
    args=p.parse_args()
    
    timelimit=600 #3 minute time limit for execution per program

    path_to_output=args.path_to_output
    dir_exists=os.path.isdir(path_to_output)
    if(not dir_exists):
        raise Exception("path for output does not exist")

    for input_file in os.listdir(args.path_to_input):
        command = args.command +" "+ args.path_to_input+"/" +input_file + ' > ' + path_to_output+"/"+input_file[:-4]+args.output_name_append
        try:
            print(command)
            proc = Popen(command,preexec_fn=os.setsid,close_fds=True,shell=True,stderr=PIPE,stdout=PIPE)
            child_stdout = proc.stdout
            child_stderr = proc.stderr
            pid = proc.pid
            start = time.time()
            end = start + timelimit
            interval = min(timelimit / 1000, .25)
            while True:
                result = proc.poll()
                if result is not None:
                    print(time.time()-start)
                    #Do stuff with output
                    out = child_stdout.read()
                    if(VERBOSE==True):
                        outlines=str(out).split('\\n')
                        for line in outlines:
                            print(line)
                    err = child_stderr.read()
                    errlines=str(err).split('\\n')
                    for line in errlines:
                        print(line)
                    break
                if time.time() >= end:
                    print(">"+str(timelimit))
                    os.killpg(os.getpgid(pid),signal.SIGTERM)
                time.sleep(interval)

        except subprocess.CalledProcessError:
            print("Failure")

