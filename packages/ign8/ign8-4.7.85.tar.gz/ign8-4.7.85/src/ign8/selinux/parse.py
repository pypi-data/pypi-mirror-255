import requests
import pprint
import shutil

import os
import hashlib
import time
import json
import subprocess
import json

# ignore ssl warnings
requests.packages.urllib3.disable_warnings()

terminal_width, _ = shutil.get_terminal_size()

def getenv():
    myenv = {}
    myenv["IGN8_SELINUX_URL"] = os.getenv("IGN8_SELINUX_URL", "https://ignite.openknowit.com/selinux")
    return myenv

def getsetrouble():
    json_data = []
    command = [
        "journalctl",
        "-u", "setroubleshootd.service",
        "--output", "json",
        "--since", "1 day ago"
    ]

# Run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            mytmpdata = json.loads(line)
            mydata = {}
            for key in mytmpdata.keys():
                newkey = key.replace("_", "")
                mydata[newkey] = mytmpdata[key]
            json_data.append(mydata)
        return json_data
    



def digest(mystring):
    # Create a SHA-256 hash object
    sha256 = hashlib.sha256()
    # Update the hash object with the bytes representation of the concatenated string
    sha256.update(mystring.encode('utf-8'))
    # Get the hexadecimal representation of the hash
    checksum = sha256.hexdigest()

    return checksum
def calculate_checksum(hostname, event, date, time):
    # Concatenate the variables into a single string
    data_to_hash = f"{hostname}{event}{date}{time}"

    # Create a SHA-256 hash object
    sha256 = hashlib.sha256()

    # Update the hash object with the bytes representation of the concatenated string
    sha256.update(data_to_hash.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    checksum = sha256.hexdigest()

    return checksum

def alligndateformat(date):
    # the input date format is MM-DD-YYYY
    # the output date format is YYYY-MM-DD
    # this function converts it to YYYYMMDD
    # this is needed for the checksum
    mysplit = date.split('/')
    try:
        date = "%s-%s-%s" % (mysplit[2], mysplit[0], mysplit[1])
    except:
        date = None

    return date

def create_suggestion(suggestion):
    mydigestedsuggestion = digest(suggestion['solution'])
    suggestion['digest'] = mydigestedsuggestion
    suggestion['lastseen'] = time.strftime("%Y-%m-%d")
    if os.path.exists("/tmp/ign8/selinux/%s" % mydigestedsuggestion):
        return True

    myenv = getenv()
    url = myenv['IGN8_SELINUX_URL'] + '/api/suggestion/upload/'  # Replace with your API endpoint URL
    response = requests.post(url, json=suggestion, verify = False)
    if response.status_code == 201:
        open("/tmp/ign8/selinux/%s" % mydigestedsuggestion, 'w').close()
        return True
    else:
        if response.status_code == 200:
            return True
        else:
            if response.status_code == 400:
                return True
            else:
                print(f"Failed to upload test event. Status code: {response.status_code}")
                print(response.status_code)
                print(response.text)
                print(response.reason)



def create_message(myrawmessage):
    try:
        mydigest = digest(myrawmessage['MESSAGE'])  
    except: 
        print("Failed to create message error in digest")
    if os.path.exists("/tmp/ign8/selinux/%s" % mydigest):
        return True
    
    

    
    try:
        lastseen = myrawmessage['REALTIMETIMESTAMP']
    except:
        lastseen = 0
    count = 0
    message = myrawmessage['MESSAGE']
    completemessage = create_complete_message(message)
    hostname = myrawmessage['HOSTNAME']
    machineid = myrawmessage['MACHINEID']
    mymessage = {}
    mymessage["digest"] = mydigest
    mymessage["message"] = message
    mymessage["completemessage"] = completemessage
    mymessage["hostname"] = hostname
    mymessage["machineid"] = machineid
    myenv = getenv()
    url = myenv['IGN8_SELINUX_URL'] + '/api/message/upload/'  # Replace with your API endpoint URL
    response = requests.post(url, json=mymessage, verify = False)

    if response.status_code == 201:
        open("/tmp/ign8/selinux/%s" % mydigest, 'w').close()
        return True
    else:
        if response.status_code == 200:
            open("/tmp/ign8/selinux/%s" % mydigest, 'w').close()
            return True
        else:
            if response.status_code == 400:
                open("/tmp/ign8/selinux/%s" % mydigest, 'w').close()
                return True
            else:
                print(f"Failed to upload test event. Status code: {response.status_code}")
                print(response.status_code)
                print(response.text)
                print(response.reason)

def create_selinux(hostdata):
    print("create_selinux")
    myenv = getenv()
    url = myenv['IGN8_SELINUX_URL'] + '/api/selinux/upload/'  # Replace with your API endpoint URL
    response = requests.post(url, json=hostdata, verify = False)
    print(response.status_code)
    print(response.reason)
    print("-------------------------")

    if response.status_code == 201:
        return True
    else:
        if response.status_code == 200:
            return True
        else:
            if response.status_code == 400:
                return True
            else:
                print(f"Failed to upload host. Status code: {response.status_code}")
                print(response.status_code)
                print(response.text)
                print(response.reason)

    



def create_setrouble(entry):
    #url = 'https://selinuxapp01fl.unicph.domain/selinux/api/setroubleshoot/upload/'  # Replace with your API endpoint URL
    url = 'https://ignite.openknowit.com:/selinux/api/setroubleshoot/upload/'  # Replace with your API endpoint URL
    #test json string is in a file called testsetrouble.json
    response = requests.post(url, json=entry, verify = False)
    if response.status_code == 201:
        return True
    else:
        if response.status_code == 200:
            return True
        else:
            if response.status_code == 400:
                return True
            else:
                print(f"Failed to upload test event. Status code: {response.status_code}")
                print(response.status_code)
                print(response.text)
                print(response.reason)

def examinemessage(myjson):
    # we need to find sugestions in the message
    suggestfound = False
    suggetsmessages = {}
    suggestnumber = 0
    myjson['digest'] = digest(myjson['MESSAGE'])
    create_message(myjson)

    for line in myjson['MESSAGE'].splitlines():
        if "suggests" in line:
            suggestfound = True
            suggestnumber += 1
            suggestkey = "suggestion%-02d" % suggestnumber
            suggetsmessages[suggestkey]  = line
        if suggestfound:
            suggestkey = "suggestion%-02d" % suggestnumber
            suggetsmessages[suggestkey] += line

#    digest = models.CharField(max_length=128)
#    status = models.CharField(max_length=128, choices=status_choices, default='initial')
#    solution = models.CharField(max_length=1024)
#    sourcecontext = models.CharField(max_length=128)
#    targetcontext = models.CharField(max_length=128)
#    targetobjecs = models.CharField(max_length=1024)
#    source = models.CharField(max_length=128)
#    sourcepath = models.CharField(max_length=128)
#    port = models.CharField(max_length=128)
#    host = models.CharField(max_length=128)
#    sourcerpmpackages = models.CharField(max_length=128)
#    targetrpmpackages = models.CharField(max_length=128)
#    selinuxpolicyrpm = models.CharField(max_length=128)
#    policytype = models.CharField(max_length=128)
#    enforcingmode = models.CharField(max_length=128)
#    hostname = models.CharField(max_length=128)
#    platform = models.CharField(max_length=512) 
#    lastseen = models.DateField(None, blank=True, null=True)
#    localid = models.CharField(max_length=128)
#    rawauditmessages = models.CharField(max_length=1024)
#
    for key in suggetsmessages.keys():
        print("key: %s" % key)
        mysuggestion = {}
        mysuggestion["digest"] = digest(suggetsmessages[key])
        mysuggestion["messagedigest"] = myjson["digest"]
        mysuggestion["solution"] = suggetsmessages[key]
        mysuggestion["hostname"] = myjson["HOSTNAME"]
        mysuggestion["lastseen"] = time.strftime("%Y-%m-%d")
        create_suggestion(mysuggestion)

        #for line in suggetsmessages[key].splitlines():  
        #    print("line: %s" % line)

def create_complete_message(message):
    print("create_complete_message")
    if "For complete SELinux messages run:" in message:
        print("found")
        mycommand = message.split("For complete SELinux messages run: ")[1]
        mycmdarray = mycommand.split()
        try:
            myoutput = subprocess.check_output(mycmdarray, text=True)
        except:
            myoutput = "%s has most possible been mitigated" % mycommand

        return myoutput






def create_metadata():
    sestatus_output = subprocess.check_output(['sestatus'], text=True)
    # Parse the output to extract required information
    mymetadata = {}
#    hostname = models.CharField(max_length=128, primary_key=True)
#    detected = models.DateField()
#  updated = models.DateField()
#    status = models.CharField(max_length=50, default='active')
#    mount = models.CharField(max_length=50, blank=True, null=True)
#    rootdir = models.CharField(max_length=50, blank=True, null=True)
#    policyname = models.CharField(max_length=50, blank=True, null=True)
#    current_mode = models.CharField(max_length=50, blank=True, null=True)
#    configured_mode = models.CharField(max_length=50, blank=True, null=True)
#    mslstatus = models.CharField(max_length=50, blank=True, null=True)
#    memprotect = models.CharField(max_length=50, blank=True, null=True)
#    maxkernel = models.CharField(max_length=50,  blank=True, null=True)
#    total = models.CharField(max_length=50, blank=True, null=True)
#   preventions = models.CharField(max_length=50, blank=True, null=True)
#    messages = models.CharField(max_length=50, blank=True, null=True)
    mymetadata["hostname"] = os.getenv("HOSTNAME")
    mymetadata["detected"] = time.strftime("%Y-%m-%d")
    mymetadata["updated"] = time.strftime("%Y-%m-%d")
    mymetadata["status"] = sestatus_output.split("SELinux status:")[1].split()[0].strip('\n')
    mymetadata["mount"] = sestatus_output.split("SELinuxfs mount:")[1].split()[0].strip('\n')
    mymetadata["rootdir"] = sestatus_output.split("SELinux root directory:")[1].split()[0].strip('\n')
    mymetadata["policyname"] = sestatus_output.split("Loaded policy name:")[1].split()[0].strip('\n')
    mymetadata["current_mode"] = sestatus_output.split("Current mode:")[1].split()[0].strip('\n')
    mymetadata["configured_mode"] = sestatus_output.split("Mode from config file:")[1].split()[0].strip('\n')
    mymetadata["mslstatus"] = sestatus_output.split("Policy MLS status:")[1].split()[0].strip('\n')
    mymetadata["memprotect"] = sestatus_output.split("Memory protection checking:")[1].split()[0].strip('\n')
    mymetadata["maxkernel"] = sestatus_output.split("Max kernel policy version:")[1].split()[0].strip('\n')
    mymetadata["total"] = 0
    mymetadata["preventions"] = 0
    mymetadata["messages"] = 0
    create_selinux(mymetadata)









def parse():
    create_metadata()
    # ensure the directory exists
    if not os.path.exists("/tmp/ign8/selinux"):
        os.makedirs("/tmp/ign8/selinux")

    setroubles = getsetrouble()
    for myjson in setroubles:
        mandatotyfields = [
                            "BOOTID",
                            "CAPEFFECTIVE",
                            "CMDLINE",
                            "CODEFILE",
                            "CODEFUNC",
                            "CODELINE",
                            "COMM",
                            "CURSOR",
                            "EXE",
                            "GID",
                            "HOSTNAME",
                            "INVOCATIONID",
                            "JOBRESULT",
                            "JOBTYPE",
                            "MACHINEID",
                            "MESSAGE",
                            "MESSAGEID",
                            "MONOTONICTIMESTAMP",
                            "OBJECTPID",
                            "PID",
                            "PRIORITY",
                            "REALTIMETIMESTAMP",
                            "SELINUXCONTEXT",
                            "SOURCEREALTIMETIMESTAMP",
                            "SYSLOGFACILITY",
                            "SYSLOGIDENTIFIER",
                            "SYSTEMDCGROUP",
                            "SYSTEMDINVOCATIONID",
                            "SYSTEMDSLICE",
                            "SYSTEMDUNIT",
                            "TRANSPORT",
                            "UID",
                            "UNIT"
            ]  
        for field in mandatotyfields:
            try:
                test = myjson[field] 
            except:
                myjson[field] = 0

        if myjson["MESSAGE"] is not None:
            mycut = terminal_width  - 15

            if len(myjson['MESSAGE'].replace("\n",";")) > terminal_width - 15:
                cutmessage = myjson['MESSAGE'].replace("\n", ";")[:mycut] + "..."
            else:
                cutmessage = myjson['MESSAGE'].replace("\n", ";")
            if "SELinux is preventing" in myjson["MESSAGE"]:
                examinemessage(myjson)

                mydigest = digest(myjson["MESSAGE"])
                myjson["digest"] = mydigest
                # if the file exists, the event has been uploaded
                if not os.path.exists("/tmp/ign8/selinux/%s" % mydigest):
                    if create_setrouble(myjson):
                        # print the fisrt 100 characters of the message
                        print("OK    : %s" % cutmessage) 
                        #create a file in /tmp/ign8/selinux with the digest as filename
                        # this is used to keep track of what has been uploaded
                        # if the file exists, the event has been uploaded
                        # if the file does not exist, the event has not been uploaded
                        # this is needed for the checksum
                        myfilename = "/tmp/ign8/selinux/%s" % mydigest
                        if not os.path.exists(myfilename):
                            with open(myfilename, 'w') as outfile:
                                json.dump(myjson, outfile)


                    else:
                        
                        print("ERROR : %s" % cutmessage)
                else:
                    print("IGNORE: %s" % cutmessage)
                    


                



def main():
    print("Ignite SELinux parser")





                
if __name__ == '__main__':


    main()

