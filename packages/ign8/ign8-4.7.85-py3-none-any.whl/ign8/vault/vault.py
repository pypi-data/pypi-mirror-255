import os
import requests
import pprint
from ..common import prettyllog



def getenv(myenv):
    myenv['VAULT_URL'] = os.environ.get("IGN8_VAULT_URL", None)
    myenv['VAULT_TOKEN'] = os.environ.get("IGN8_VAULT_TOKEN", None)
    return myenv



def checkaccess():
    myenv = getenv({})
    if myenv['VAULT_URL'] is None:
        prettyllog("vault", "checkaccess", myenv['VAULT_URL'], "-", "000", "Environment not set vault url", "ERROR")
        return None
    if myenv['VAULT_TOKEN'] is None:
        prettyllog("vault", "checkaccess", myenv['VAULT_URL'], "-", "000", "Environment not set vault token", "ERROR")
        return None
    
    headers = {'X-Vault-Token': myenv['VAULT_TOKEN']}   
    checkaccess = requests.get(myenv['VAULT_URL']+"/api/v1/healthcheck/", headers=headers, verify=False)
    if checkaccess.status_code == 200:
        return True
    else:
        print("Vault access failed")
        return None


def getlogin(path):
    if checkaccess():

        vaultlogin = requests.get("http://localhost:8000/api/v1/vault/login/?path=" + path)
        if vaultlogin.status_code == 200:
            return vaultlogin.json()
        else:
            return None
    else:
        return None
    