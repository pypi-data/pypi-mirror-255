import argparse
import requests
from ..common import prettyllog
from .terraform import pluging_install




def main():
    usage =  "Usage:"
    usage += " ign8_terraform <action> \n\n"
    usage += "Actions:\n"
    usage += "           plugin_install\n"
    usage += "           service\n\n"
    usage += "           2024 ign8.it "
    parser = argparse.ArgumentParser(description="Keep ign8 and automate", usage=usage)
    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup netbox')
    args = parser.parse_args()

    if args.action[0] == "plugin_install":
        pluging_install()
    elif args.action[0] == "service":
        print("Service")

    


