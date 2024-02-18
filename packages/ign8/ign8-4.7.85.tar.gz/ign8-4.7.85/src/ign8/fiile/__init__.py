import os
import argparse
from .file import file


from ..common import prettyllog

def main():
    parser = argparse.ArgumentParser(description="ignite files", usage="ign8_file <action> \n\n \
               \
               version : 0.1.2   \n                                              \
               actions:\n                                                      \
               follow        follow symlinks \n  \
               \
               2024 Knowit Miracle\
               ")
    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup jenkis')
    args = parser.parse_args()
    ready = False
    print("check if we are ready to go")


    if args.action[0] == "follow":
        try:
            physfile = file.follow(args.action[1])
            return physfile
        except:
            return False


