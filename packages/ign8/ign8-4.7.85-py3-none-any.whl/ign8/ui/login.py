import os
import sys
import pprint
from ..common import prettyllog
import subprocess
import hvac
import psutil


def is_firefox_running():
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == 'firefox-esr' or process.info['name'] == 'firefox' or process.info['name'] == 'firefox-bin' or process.info['name'] == 'firefox-esr-bin':
            return True
    return False



def writekv(path, keypair):
  ign8_vault_url  = os.environ.get("VAULT_URL", "https://vault.openknowit.com")
  ign8_vault_token = os.environ.get("VAULT_TOKEN", "s.5Y9pZ4x6y3sZ4y3s")
  client = hvac.Client(
    url=ign8_vault_url,
    token=ign8_vault_token,
  )
  create_response = client.secrets.kv.v2.create_or_update_secret(
    path=path,
    secret=dict(keypair),
  )
  print('Secret written successfully.')
  return 0
def firefox_cookies():
  prettyllog("ui", "login", "firefox_cookies", "extracting firefox cookies", 000 , "Start", severity="DEBUG")
  # change to my home directory
  mydir = os.path.expanduser("~")+ "/.mozilla/firefox"

  os.system(mydir)
  prettyllog("ui", "login", "firefox_cookies", "changed to firefox directory", 000 , "Start", severity="DEBUG")
  filename = find_file(mydir, "cookies.sqlite")
  # copy the file to my home directory/tmp for processing
  myhome = os.path.expanduser("~")
  mydir = myhome + "/tmp"

  os.system("mkdir -p " + mydir + '>/dev/null 2>&1' )
  os.system("cp " + filename + " " + mydir + "/cookies.tmp.sqlite")
  prettyllog("ui", "login", "firefox_cookies", "copied cookies.sqlite to tmp", 000 , "Start", severity="DEBUG")
  # connect to the database

  mysql = "SELECT * FROM moz_cookies"
  command =  ["sqlite3", "/home/jho/tmp/cookies.tmp.sqlite", mysql]
  mycookiedata = subprocess.run(command, capture_output=True)
  mysplit = mycookiedata.stdout.splitlines()
  for line in mysplit:
    line = line.decode('utf-8')
    mysplit = line.split("|")
    count = 0
    for item in mysplit:
      print(item)
      count = count + 1









  prettyllog("ui", "login", "firefox_cookies", "executed SELECT * FROM moz_cookies", 000 , "Start", severity="DEBUG")
  # remove the file
  prettyllog("ui", "login", "firefox_cookies", "removed cookies.sqlite", 000 , "Start", severity="DEBUG")
  return 0







def find_file(directory, filename):
    for root, dirs, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None


def extractcookie():
  # change to my home directory
  # is firefox running?
  if is_firefox_running():
    firefox_cookies()

  else:
    print("firefox is not running")
    return 0





def main():
  prettyllog("ui", "login", "init", "initializing login", 000 , "Start", severity="DEBUG")
  keypair = {"username": "admin", "password": "admin123"}  
  writekv("igniteui", keypair)
  extractcookie()
  return 0

