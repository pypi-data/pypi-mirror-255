from . import parse
import argparse
from ..common import prettyllog




def main():
    parser = argparse.ArgumentParser(description="ignite selinux", usage="ign8_selinux <action> \n\n \
               \
               version : 0.1.2 selinux  \n                                              \
               actions:\n                                                      \
               parse        parse \n  \
               \
               2024 Knowit Miracle\
               ")

    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup jenkis')
    args = parser.parse_args()
    ready = False
    print("check if we are ready to go")

    if args.action[0] == "parse":
        print("list_dags pitv")
        parse.parse()


