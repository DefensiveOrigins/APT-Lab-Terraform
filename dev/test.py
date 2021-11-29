import argparse
import csv
import json
import os
import sys

import azurerm
from datetime import time
from azure.cli.core import get_default_cli
from haikunator import Haikunator

location = ""
# Load Azure app defaults
try:
    with open('azurermconfig.json') as config_file:
        config_data = json.load(config_file)
except FileNotFoundError:
    sys.exit('Error: Expecting azurermconfig.json in current folder')
tenant_id = config_data['tenantId']
app_id = config_data['appId']
app_secret = config_data['appSecret']
subscription_id = config_data['subscriptionId']

# authenticate
access_token = azurerm.get_access_token(tenant_id, app_id, app_secret)

def az_cli(args_str):
    args = args_str.split()
    cli = get_default_cli()
    cli.invoke(args)
    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise cli.result.error
    return True


def csvParser(csvpath):
    with open(csvpath) as csvfile:
        file_read = csv.reader(csvfile)

        vmlist = list(file_read)
        vmlist.pop(0)
        print(vmlist)

        for element in vmlist:
            createVMs(element)

def createNSG(rgname, vname, prefix):
    # create NSG
    nsg_name = prefix + 'nsg'
    print('Creating NSG: ' + nsg_name)
    rmreturn = azurerm.create_nsg(access_token, subscription_id, rgname, nsg_name, location)
    nsg_id = rmreturn.json()['id']
    print('nsg_id = ' + nsg_id)

    # create NSG rule
    nsg_rule = 'ssh'
    print('Creating NSG rule: ' + nsg_rule)
    rmreturn = azurerm.create_nsg_rule(access_token, subscription_id, rgname, nsg_name, nsg_rule,
                                       description='ssh rule', destination_range='22')
    print(rmreturn)
    print(json.dumps(rmreturn.json(), sort_keys=False, indent=2, separators=(',', ': ')))

def createVNET(rgname, prefix, nsg_id):
    # create VNET
    vnetname = prefix + 'vnet'
    print('Creating VNet: ' + vnetname)
    rmreturn = azurerm.create_vnet(access_token, subscription_id, rgname, vnetname, location,
                                   nsg_id=nsg_id)
    print(rmreturn)
    # print(json.dumps(rmreturn.json(), sort_keys=False, indent=2, separators=(',', ': ')))
    subnet_id = rmreturn.json()['properties']['subnets'][0]['id']
    print('subnet_id = ' + subnet_id)

def createPublicIP(rgname, prefix):
     # create public IP address
    public_ip_name = prefix + 'ip'
    dns_label = prefix + 'ip'
    print('Creating public IP address: ' + public_ip_name)
    rmreturn = azurerm.create_public_ip(access_token, subscription_id, rgname, public_ip_name,
                                        dns_label, location)
    print(rmreturn)
    ip_id = rmreturn.json()['id']
    print('ip_id = ' + ip_id)

    print('Waiting for IP provisioning..')
    waiting = True
    while waiting:
     ipa = azurerm.get_public_ip(access_token, subscription_id, rgname, public_ip_name)
     if ipa['properties']['provisioningState'] == 'Succeeded':
         waiting = False
     time.sleep(1)

def createNIC(rgname,vmdata, ip_id, subnet_id):
    # create NIC
    nic_name = vmdata[0] + 'nic'
    print('Creating NIC: ' + nic_name)
    rmreturn = azurerm.create_nic(access_token, subscription_id, rgname, nic_name, ip_id,
                                  subnet_id, location)
    # print(json.dumps(rmreturn.json(), sort_keys=False, indent=2, separators=(',', ': ')))
    nic_id = rmreturn.json()['id']

    print('Waiting for NIC provisioning..')
    waiting = True
    while waiting:
        nic = azurerm.get_nic(access_token, subscription_id, rgname, nic_name)
        if nic['properties']['provisioningState'] == 'Succeeded':
            waiting = False
        time.sleep(1)

def createVMs(rgname, vmdata, nic_id):
    # initialize haikunator
    hkn = Haikunator()

    if vmdata[5] == 'Y':
        print("This is a DC")
    print("This is NOT a DC")
    # create VM
    vm_name = vmdata[0]
    vm_size = vmdata[1]

    print(vm_name)
    print(vm_size)

    ### TODO Tried fetching the publisher and offer from SKU but I think authenticaiton fails
    #azcommand = "vm image list -s \"" + vmdata[2] + "\""
    #vmparameterJSON = az_cli(azcommand)

    #print(vmparameterJSON)
    #vmdictionary = json.loads(vmparameterJSON)
    #print(vmdictionary["publisher"])

    publisher = ""
    offer = ""

    # This will not scale well but works for now
    match vmdata[2]:
        case "2016-Datacenter":
            publisher = "MicrosoftWindowsServer"
            offer = "WindowsServer"
        case "18.04-LTS":
            publisher = "Canonical"
            offer = "UbuntuServer"
        case "20h1-pro":
            publisher = "MicrosoftWindowsDesktop"
            offer = "Windows-10"

    sku = vmdata[2]

    version = 'latest'
    if not vmdata[4]:
        version = vmdata[4]

    username = vmdata[5]
    password = hkn.haikunate(delimiter=',')  # creates random password
    print('password = ' + password)
    print('Creating VM: ' + vm_name)
    rmreturn = azurerm.create_vm(access_token, subscription_id, rgname, vm_name, vm_size,
                                 publisher, offer, sku, version, nic_id, location,
                                 username=username, password=password)
    print(rmreturn)
    print(json.dumps(rmreturn.json(), sort_keys=False, indent=2, separators=(',', ': ')))


def main():
    parser = argparse.ArgumentParser(description='Creates Azure resources for Lab environment with terraform')
    parser.add_argument('-m', help='Public IP Addresses for management access rules(ex. 1.1.1.1 or 1.1.1.0/24',
                        metavar='input_mgmt', dest='mgmtip', type=str, nargs='+', required=False)
    parser.add_argument('-d', '-destroy',
                        help='Will use terraform Destroy to destroy everything created by this script in Azure',
                        action='store_true', dest='destroy_switch', required=False)
    parser.add_argument('-p', '-prefix',
                       help='Prefix for different resources in the lab. Examples could be lab, test, ...',
                       dest='prefix', required=True)
    # parser.add_argument('-r','-region', help='Set the region where you want the lab to be deployed. Default "westeurope"', dest='region', type=str, required=False)
    # parser.add_argument('-u','-username', help='Specify the username of the domain administrator. Default: myadmin',dest='username', type=str, required=False)
    # parser.add_argument('-p','-password', help='Specify the password of the domain administrator. Default: Admin123!. Remember to follow the default password complexity --> https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/password-must-meet-complexity-requirements',dest='password', type=str, required=False)
    parser.add_argument('-c', '-csv-file',
                        help='Specify the path the .csv file. This file enables bulk creation. The user can define all VMs in the .csv template and create them by parsing that file. It needs to follow a certain structure. You can find the template at https://github.com/oerlex/APT-Lab-Terraform',
                        dest='csv', type=str, required=False)
    args = parser.parse_args()

    if args.destroy_switch:
        print(
            "===This will use Terraform to DESTROY the Lab environment that was created in Azure====== \n This will 'un-build' the lab and all the data will be destroyed")
        time.sleep(3)
        os.system("cd LABS && terraform destroy")
    else:
        def split_args(arg):
            try:
                arg = " ".join(arg)
                arg = arg.replace(" ", "")
                if any("," in item for item in arg):
                    arg = arg.split(",")
                if type(arg) is list:
                    return arg
                else:
                    return [arg]
            except TypeError:
                # this is thrown if a None is passed in for 'arg'
                return None

        mgmtip = args.mgmtip
        prefix = args.prefix
        # region=args.region
        # username=args.username
        # password=args.password
        csvpath = args.csv

        csvParser(csvpath)


main()
