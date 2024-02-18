from . import pypi
import argparse

def main():
    parser = argparse.ArgumentParser(description="Keep ign8 and automate", usage="ign8_dns <action> \n\n \
               \
               version : 0.0.0 BETA \n                                              \
               actions:\n                                                      \
               versions   list pypi versions of a pypi package \n  \
               \
               2023 Knowit Miracle\
               ")
    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup netbox')
    args = parser.parse_args()
    ready = False
    print("check if we are ready to go")

    if args.action[0] == "versions":
        pypi.versions(args)

    if args.action[0] == "poetry-dependencies":
        pypi.poetry_dependensies()



    





