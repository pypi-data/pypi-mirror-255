import os
import json
from ..common import prettyllog


def usage():
  # export the environment variables
  print("export KALM_ZABBIX_URL=\"\"")
  print("export KALM_ZABBIX_TOKEN=\"\"")
  print("export KALM_ZABBIX_SSL=\"\"")


def  get_env():
  prettyllog("get_env", "Read", "Environment", "kalm" ,"000", "Reading zabbix environment", "info")
  myenv = {}
  myenv['subproject'] = {}
  try:
    myenv['KALM_ZABBIX_URL'] = os.getenv("KALM_ZABBIX_URL")
    myenv['KALM_ZABBIX_TOKEN'] = os.getenv("KALM_ZABBIX_TOKEN")
    myenv['KALM_ZABBIX_SSL'] = os.getenv("KALM_ZABBIX_SSL", "false")
    myenv['KALM_WORKDIR'] = os.getenv("KALM_WORKDIR", "/")

  except KeyError as key_error:
    print(key_error)
    usage()
    raise SystemExit("Unable to get environment variables.")
  if myenv['KALM_ZABBIX_URL'] == None:
    usage()
    raise SystemExit("Unable to get environment variables.")
  if myenv['KALM_ZABBIX_TOKEN'] == None:
    usage()
    raise SystemExit("Unable to get environment variables.")
  
  if myenv['KALM_ZABBIX_SSL'] == "false" or myenv['KALM_ZABBIX_SSL'] == "False" or myenv['KALM_ZABBIX_SSL'] == "FALSE" or myenv['KALM_ZABBIX_SSL'] == "no" or myenv['KALM_ZABBIX_SSL'] == "NO" or myenv['KALM_ZABBIX_SSL'] == "No":
    myenv['KALM_ZABBIX_SSL'] = False
  else:
    myenv['KALM_ZABBIX_SSL'] = True
  if myenv['KALM_ZABBIX_URL'][-1] == "/":
    myenv['KALM_ZABBIX_URL'] = myenv['KALM_ZABBIX_URL'][:-1]

  

  # list all files in /etc 
  if os.path.exists(myenv['KALM_WORKDIR']) == False:
    os.mkdir(myenv['KALM_WORKDIR'])
  files = os.listdir(myenv['KALM_WORKDIR'] + "/etc/kalm")

  if os.path.exists(myenv['KALM_WORKDIR'] + "/etc/kalm/zabbix.json") == False:
    raise SystemExit("Unable to find " + myenv['KALM_WORKDIR'] +"/etc/kalm/zabbix.json")
  
  #read the zabbix json file 
  prettyllog("get_env", "Read", "zabbix.json", "kalm", "000", "Reading zabbix.json file", "info")
  conf_path = myenv['KALM_WORKDIR'] + "/etc/kalm/zabbix.json"

  if os.path.exists(conf_path):
        with open(conf_path, 'r') as json_file:
            data = json.load(json_file)
            myenv['zabbix'] = data
  return myenv
