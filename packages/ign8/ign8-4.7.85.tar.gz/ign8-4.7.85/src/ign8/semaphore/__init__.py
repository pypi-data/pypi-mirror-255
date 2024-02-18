# keep ign8 and con5entrate on your semaphores

from . import serve
import argparse

def main():
    parser = argparse.ArgumentParser(description="Keep ign8 and con5entrate on your semaphores", usage="ign8_semaphore <action> \n\n \
\
version : 0.0.2 (semaphore)\n\
actions:\n\
serve      keep ign8 and serve semaphore\n\
init       keep ign8 and init semaphore systemd service\n\
start      keep ign8 and start semaphore systemd service\n\
stop       keep ign8 and stop semaphore systemd service\n\
restart    keep ign8 and restart semaphore systemd service\n\
setup      keep ign8 and setup semaphore\n\
test       keep ign8 and test semaphore\n\
audit      keep ign8 and audit semaphore\n\
\n\
\
2023 Knowit Miracle\
")
    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup jenkis')
    args = parser.parse_args()
    ready = False

    if args.action[0] == "serve":
        serve.main()
        return 0
    

