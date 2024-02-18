import os
import sys
import pprint
from ..common import prettyllog
import subprocess





def main():
    prettyllog("ui", "ui", "ui", "new", "000", "ui")
    ign8_ui_port  = os.environ.get("IGN8_UI_PORT", "8000")
    ign8_ui_host = os.environ.get("IGN8_UI_HOST", "ign8.openknowit.com")
    ign8_ui_debug = os.environ.get("IGN8_UI_DEBUG", "True")

    # change to the ui directory
    VIR_ENV = os.environ.get("VIRTUAL_ENV", "/opt/ign8")
    os.chdir(VIR_ENV + "/lib/python3.9/site-packages/ign8/ui/project/ignite")

    print(os.getcwd())
    print(os.listdir())


    # run the server
    # python manage.py runserver

    myserver = subprocess.run(["gunicorn", "--bind", ign8_ui_host + ":" + ign8_ui_port, "--workers", "3", "ignite.wsgi -c gunicorn.conf.py --log-level=debug"])

    pprint.pprint(myserver) 

    return 0





    


                          
