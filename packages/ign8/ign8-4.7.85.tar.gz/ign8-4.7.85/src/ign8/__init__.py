import os
import sys
import redis
import time
import subprocess
import json
import argparse
import requests
from .common import prettyllog
from .main import main, serve

from .setup import setupign8






class suppress_stdout_stderr(object):
    '''
    A context manager for doing a "deep suppression" of stdout and stderr in 
    Python, i.e. will suppress all print, even if the print originates in a 
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).      

    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds =  [os.open(os.devnull,os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0],1)
        os.dup2(self.null_fds[1],2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0],1)
        os.dup2(self.save_fds[1],2)
        # Close all file descriptors
        for fd in self.null_fds + self.save_fds:
            os.close(fd)



def runme(command):
  commandlist = command.split(" ")
  result = subprocess.run(commandlist, capture_output=True)
  payload = {"returncode": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr }
  return payload


def connectiontest():
  checks=[]
  errors=[]
  if len(errors) > 0:
    prettyllog("connectiontest", "check", "connectiontest", "all", "500", "Failed", "ERROR")
    return False
  else:
    return True
    
def main():
    usage =  "Usage:"
    usage += " ign8 <action> \n\n"
    usage += "Actions:\n"
    usage += "           check\n"
    usage += "           setup\n"
    usage += "           reset\n"
    usage += "           startservice\n"
    usage += "           stopservice\n"
    usage += "           initservice\n"
    usage += "           service\n\n"
    usage += "           2024 ign8.it "
    parser = argparse.ArgumentParser(description="Keep ign8 and automate", usage=usage)
    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup netbox')
    args = parser.parse_args()
    ready = False
    ready  = connectiontest()

    if args.action[0] == "setup":
        setupign8()
    elif args.action[0] == "check":
        print("Checking")
    elif args.action[0] == "reset":
        print("Resetting")
    elif args.action[0] == "startservice":
        print("Starting Service")
    elif args.action[0] == "stopservice":
        print("Stopping Service")
    elif args.action[0] == "initservice":
        print("Initializing Service")
    elif args.action[0] == "service":
        print("Service")
        serve()



    





