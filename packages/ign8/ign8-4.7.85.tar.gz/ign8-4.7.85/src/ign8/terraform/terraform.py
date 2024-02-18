import subprocess
import os
import pprint

from ign8 import runme





def init():
    """Initialize terraform"""
    pass

def plan():
    """Run terraform plan"""
    pass

def pluging_install():
    # we need to have go installed
    # execute go version to check if go is installed
    # if go is not installed, install go
    gotest = runme("go version")
    if gotest["returncode"] != 0:
        print("Go is not installed")
        print("Installing Go")
        runme("sudo apt-get install -y golang-go")
    else:
        print("Go is installed")




  


    # we need to have terraform installed


def apply():
    """Run terraform apply"""
    pass



