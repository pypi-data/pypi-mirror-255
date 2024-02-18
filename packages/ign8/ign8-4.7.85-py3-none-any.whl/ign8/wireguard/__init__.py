from . import wireguard
import argparse

def main():
    parser = argparse.ArgumentParser(description="Keep ign8 and automate", usage="ign8_dns <action> \n\n \
               \
               version : 0.0.0 BETA \n                                              \
               actions:\n                                                      \
               refresh\n  \
               \
               2023 Knowit Miracle\
               ")
    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup wireguard')
    args = parser.parse_args()
    ready = False
    print("check if we are ready to go")

    if args.action[0] == "refresh":
        wireguard.refresh(args)




    





