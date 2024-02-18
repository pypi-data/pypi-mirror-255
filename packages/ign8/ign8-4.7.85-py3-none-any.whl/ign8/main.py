from .common import prettyllog
import os
import subprocess
import sys

def getenv(key, default):
    if key in os.environ:
        return os.environ[key]
    else:
        return default

def main():
    prettyllog("main", "check", "main", "all", "200", "Success")
    return True

def in_venv():
    return sys.prefix != sys.base_prefix


def serve():
    prettyllog("main", "check", "main", "all", "200", "Success", "info")
    if not in_venv():
        prettyllog("main", "check", "Not a virtual env", "all", "200", "Success")
        os.system("python3 -m venv /tmp/ign8_venv")
        os.system("source /tmp/ign8_venv/bin/activate")
        os.system("pip install --upgrade ign8 >/dev/null 2>&1")
        os.system("pip install --upgrade pip >/dev/null 2>&1")

    print("Starting Ign8 UI")
    print(sys.prefix)

    os.system("pip install --upgrade ign8 >/dev/null 2>&1")
    mydir = sys.prefix + "/lib/python3.9/site-packages/ign8/ui/project/ignite/"
    os.chdir(mydir)
    os.system("python manage.py makemigrations")
    os.system("python manage.py migrate")
    #p = Popen(['espeak', '-b', '1'], stdin=PIPE, stdout=DEVNULL, stderr=STDOUT)
    #gunicorn = subprocess.Popen(["gunicorn", "ignite.wsgi", "-c", "gunicorn.conf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    gunicorn = subprocess.Popen(["gunicorn", "ignite.wsgi", "-c", "gunicorn.conf"])
    prettyllog("main", "check", "main", "all", "200", "Success", "info")
    gunicorn.wait()



#    os.command("gunicorn ignite.wsgi -c gunicorn.conf")
    # change working directory to the root of the project




    return True
