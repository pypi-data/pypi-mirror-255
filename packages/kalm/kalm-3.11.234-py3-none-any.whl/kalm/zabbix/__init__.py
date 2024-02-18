from . import zabbix
import argparse

def main():
    parser = argparse.ArgumentParser(description="Keep kalm and automate zabbix", usage="kalm_zabbix <action> \n\n \
               \
                version : 0.0.2 (zabbix)\n\
                actions:\n\
                register          register server on zabbix  \n\
                hostgroup         list hostgroup data   for ZABBIX_HOSTGROUP  \n\
                hostgroups        list all known hostgroups \n\
                serve             run the kalm_zabbix_service \n\
               \
               2023 Knowit Miracle\
               ")
    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup jenkis')
    args = parser.parse_args()
    ready = False

    if args.action[0] == "status":
        return zabbix.status()
    
    if args.action[0] == "hostgroup":
        return zabbix.list_host_group()
    
    if args.action[0] == "hostgroups":
        return zabbix.list_host_groups()
    
    if args.action[0] == "register":
        return zabbix.register()    
    
    if args.action[0] == "serve":
        return zabbix.serve()    

    return 0

    

    







