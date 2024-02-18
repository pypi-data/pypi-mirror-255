import argparse
import os


from ..common import prettyllog
from . import serve, start, stop, status, selinux, firewall, setup, login, logout


def main():
    parser = argparse.ArgumentParser(description="Keep ign8 and automate", usage="ign8_ui <action> \n\n\
\
                version : 0.0.1 \n\
                actions:\n\
                serve                        run the service as in systemd but with stdout on the terminal\n\
                start                        start the service in systemd\n\
                stop                         stop the systemd\n\
                status                       Show the status of the systemd services\n\
                selinux                      Ensure selinux is configured\n\
                firewall                     Ensure Firewall is configured\n\
                setup                        Setup server to host ign8_ui\n\
                login                        enable webserver login\n\
                logout                       disable webserver login\n\
\
                2024 Knowit\n\
                ")
    



    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup netbox')
    args = parser.parse_args()
    ready = False
    if args.action[0] == "serve":
        serve.main()
        return 0
    
    if args.action[0] == "start":
        start.main()
        return 0
    
    if args.action[0] == "stop":
        stop.main()
        return 0
    
    if args.action[0] == "status":
        status.main()
        return 0
    
    if args.action[0] == "selinux":
        selinux.main()
        return 0
    
    if args.action[0] == "firewall":
        firewall.main()
        return 0
    
    if args.action[0] == "setup":
        setup.main()
        return 0
    
    if args.action[0] == "login":
        login.main()
        return 0
    
    if args.action[0] == "logout":
        logout.main()
        return 0
    
    
    

        
