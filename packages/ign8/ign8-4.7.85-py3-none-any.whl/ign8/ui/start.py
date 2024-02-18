import os
import sys
import pprint
from ..common import prettyllog
import subprocess
import hvac





def main():
    prettyllog("ui", "ui", "ui", "new", "000", "ui")
    ign8_vault_url  = os.environ.get("IGN8_VAULT_URL", "http://vault.openknowit.com")
    ign8_vault_token = os.environ.get("IGN8_VAULT_TOKEN", "s.5Y9pZ4x6y3sZ4y3s")

    # change to my home directory
    os.chdir("~")
    # we need to check if the vault is already mounted
    client = hvac.Client(
      url=ign8_vault_url,
      token=ign8_vault_token,
    )

    create_response = client.secrets.kv.v2.create_or_update_secret(
    path='my-secret-password',
    secret=dict(password='Hashi123'),
    )

    print('Secret written successfully.')




    return 0