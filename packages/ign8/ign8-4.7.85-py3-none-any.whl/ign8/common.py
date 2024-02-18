import os
import datetime
import subprocess 


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    DEBUG   = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    INFO    = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


VERIFY_SSL = os.getenv("VERIFY_SSL", "false")
if VERIFY_SSL == "false" or VERIFY_SSL == "False" or VERIFY_SSL == "FALSE" or VERIFY_SSL == "no" or VERIFY_SSL == "NO" or VERIFY_SSL == "No":
  VERIFY_SSL = False
else:
  VERIFY_SSL = True

def line_in_file(file_path, search_text):
    with open(file_path, 'r') as f:
        for line in f:
            if search_text in line:
                return True
    return False
def runme(command):
  commandlist = command.split(" ")
  result = subprocess.run(commandlist, capture_output=True)
  payload = {"returncode": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr }
  return payload

    

def get_file_content(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def get_file_content_lines(file_path):
    with open(file_path, 'r') as f:
        return f.readlines()
    
# 127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
    #    127.0.0.1 is the IP address of the client (remote host) which made the request to the server.
    # user-identifier is the RFC 1413 identity of the client. Usually "-".
    #frank is the userid of the person requesting the document. Usually "-" unless .htaccess has requested authentication.
    #[10/Oct/2000:13:55:36 -0700] is the date, time, and time zone that the request was received, by default in strftime format %d/%b/%Y:%H:%M:%S %z.
    #"GET /apache_pb.gif HTTP/1.0" is the request line from the client. The method GET, /apache_pb.gif the resource requested, and HTTP/1.0 the HTTP protocol.
    #200 is the HTTP status code returned to the client. 2xx is a successful response, 3xx a redirection, 4xx a client error, and 5xx a server error.
    #2326 is the size of the object returned to the client, measured in bytes.
# we need to rewrite prettylog to use this format
    

    

def prettyllog(function, action, item, organization, statuscode, text, severity="INFO"):
  silence = False
  try:
    if os.getenv("IGN8_SILENCE", "false").lower() == "true":
      silence = True
  except:
    silence = False
    
  if silence:
    return True

  d_date = datetime.datetime.now()
  reg_format_date = d_date.strftime("%Y-%m-%d %I:%M:%S %p")
  if severity == "INFO":
    print(f"{bcolors.INFO}%-20s: %-12s %20s %-50s %-20s %-4s %-50s " %( reg_format_date, function,action,item,organization,statuscode, text))
  elif severity == "WARNING":
    print(f"{bcolors.WARNING}%-20s: %-12s %20s %-50s %-20s %-4s %-50s " %( reg_format_date, function,action,item,organization,statuscode, text))
  elif severity == "ERROR":
    print(f"{bcolors.FAIL}%-20s: %-12s %20s %-50s %-20s %-4s %-50s " %( reg_format_date, function,action,item,organization,statuscode, text))
  elif severity == "DEBUG":
    print(f"{bcolors.OKCYAN}%-20s: %-12s %20s %-50s %-20s %-4s %-50s " %( reg_format_date, function,action,item,organization,statuscode, text))
  else:
    print(f"{bcolors.INFO}%-20s: %-12s %20s %-50s %-20s %-4s %-50s " %( reg_format_date, function,action,item,organization,statuscode, text))
  print(f"{bcolors.ENDC}", end='')
  return True
