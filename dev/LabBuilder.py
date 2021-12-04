import urllib,json, subprocess, os, errno, shutil, argparse, configparser, csv, time
from requests import get

############ Setup section for students
#

# By default your VMs will be deployed to Azure Cloud in a Central US data center.
# For a list of valid, alternative locations run the following command:
#   az account list-locations -o table
#
# Apply the desired value from the "name" column in the region variable.

region="westeurope"
username="myadmin"
password="Admin123!"

# To deploy your VMs to Azure Cloud, you will first need to create an Azure
# Service Principal and a "secret token". These will be used by this script to
# Terraform your lab environment.
# See -> https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/service_principal_client_secret
#
# BEWARE!
# The following information allows direct login to your Azure Cloud environment!
# Treat this file as highly confidential!

subscription_id = "xxxxx"
client_id       = "yyyy"
client_secret   = "zzzz"
tenant_id       = "aaaa"

def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)
def readmastertf(masterfile):
    fileaccess = open(masterfile, "r")
    filecontent = fileaccess.read()
    fileaccess.close()
    return filecontent

def buildmain(mgmtip):
    staticinfo='''provider "azurerm" {

    features{}
    subscription_id = "subid"
    client_id       = "clid"
    client_secret   = "clse"
    tenant_id       = "tenid"
    }
        locals {
        resource_group_name   = "class-resources"
        master_admin_username ="myadmin"
        master_admin_password ="Admin123!"
        master_domain         ="pentest.lab"
    }
    '''
    buildinfo='''

    resource "azurerm_resource_group" "stu" {
      name     = local.resource_group_name
      location = "regionalregion"
    }

    module "stu-network" {
      source              = "./modules/network"
      prefix              = "stu"
      resource_group_name = azurerm_resource_group.stu.name
      location            = azurerm_resource_group.stu.location
    }

    module "stu-DC" {
      source                        = "./modules/active-directory"
      resource_group_name           = azurerm_resource_group.stu.name
      location                      = azurerm_resource_group.stu.location
      prefix                        = "stu"
      subnet_id                     = module.stu-network.domain_subnet_id
      active_directory_domain       = local.master_domain
      active_directory_netbios_name = "LABS"
      admin_username                = local.master_admin_username
      admin_password                = local.master_admin_password
    }

    module "stu-client" {
      source                    = "./modules/windows-client1"
      resource_group_name       = azurerm_resource_group.stu.name
      location                  = azurerm_resource_group.stu.location
      prefix                    = "stu"
      subnet_id                 = module.stu-network.domain_clients_subnet_id
      active_directory_domain   = local.master_domain
      active_directory_username = local.master_admin_username
      active_directory_password = local.master_admin_password
      admin_username            = local.master_admin_username
      admin_password            = local.master_admin_password
      networksec_group          = azurerm_network_security_group.stu-rdp.id
    }

    output "stu_Public_IP" {
      value = module.stu-client.public_ip_address
    }

    module "stu-linux" {
      source                    = "./modules/linux"
      resource_group_name       = azurerm_resource_group.stu.name
      location                  = azurerm_resource_group.stu.location
      prefix                    = "stu"
      subnet_id                 = module.stu-network.domain_subnet_id
      active_directory_domain   = local.master_domain
      active_directory_username = local.master_admin_username
      active_directory_password = local.master_admin_password
      admin_username            = local.master_admin_username
      admin_password            = local.master_admin_password
    }

    resource "azurerm_network_security_group" "stu-rdp" {
      name     = "stu-rdp"
      resource_group_name  = azurerm_resource_group.stu.name
      location = "regionalregion"
      security_rule{
        name                       = "stu-rdp-rule-mgmt"
        direction                  = "Inbound"
        access                     = "Allow"
        priority                   = 200
        source_address_prefix      = "mgmtip"
        source_port_range          = "*"
        destination_address_prefix = "*"
        destination_port_range     = "3389"
        protocol                   = "TCP"
      }
      security_rule{
        name                       = "stu-internal-in"
        direction                  = "Inbound"
        access                     = "Allow"
        priority                   = 300
        source_address_prefix      = "10.10.0.0/16"
        source_port_range          = "*"
        destination_address_prefix = "*"
        destination_port_range     = "*"
        protocol                   = "*"
      }
      security_rule{
        name                       = "stu-internal-out"
        direction                  = "Outbound"
        access                     = "Allow"
        priority                   = 400
        source_address_prefix      = "10.10.0.0/16"
        source_port_range          = "*"
        destination_address_prefix = "*"
        destination_port_range     = "*"
        protocol                   = "*"
        }
    }'''

    maintf = open('./LABS/main.tf', 'a+')
    staticinfo=staticinfo.replace('subid',subscription_id)
    staticinfo=staticinfo.replace('clid',client_id)
    staticinfo=staticinfo.replace('clse',client_secret)
    staticinfo=staticinfo.replace('tenid',tenant_id)
    maintf.write(staticinfo)
    tmp=buildinfo
    tmp=tmp.replace('mgmtip',mgmtip[0])
    tmp=tmp.replace('regionalregion',region)
    maintf.write(tmp)



def main():
    parser = argparse.ArgumentParser(description='Creates Azure resources for Lab environment with terraform')
    parser.add_argument('-m', help='Public IP Addresses for management access rules(ex. 1.1.1.1 or 1.1.1.0/24',
        metavar='input_mgmt', dest='mgmtip', type=str, nargs='+', required=False)
    parser.add_argument('-d','-destroy', help='Will use terraform Destroy to destroy everything created by this script in Azure',  action='store_true', dest='destroy_switch',  required=False)
    parser.add_argument('-r','-region', help='Set the region where you want the lab to be deployed. Default "westeurope"', dest='region', type=str, required=False)
    parser.add_argument('-u','-username', help='Specify the username of the domain administrator. Default: myadmin',dest='username', type=str, required=False)
    parser.add_argument('-p','-password', help='Specify the password of the domain administrator. Default: Admin123!. Remember to follow the default password complexity --> https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/password-must-meet-complexity-requirements',dest='password', type=str, required=False)
    parser.add_argument('-c','-csv-file', help='Specify the path the .csv file. This file enables bulk creation. The user can define all VMs in the .csv template and create them by parsing that file. It needs to follow a certain structure. You can find the template at https://github.com/oerlex/APT-Lab-Terraform')
    args=parser.parse_args()

    if args.destroy_switch:
        print("===This will use Terraform to DESTROY the Lab environment that was created in Azure====== \n This will 'un-build' the lab and all the data will be destroyed")
        time.sleep(3)
        os.system("cd LABS && terraform destroy")
    else:
      def split_args(arg):
          try:
              arg=" ".join(arg)
              arg=arg.replace(" ", "")
              if any("," in item for item in arg):
                  arg = arg.split(",")
              if type(arg) is list:
                  return arg
              else:
                  return [arg]
          except TypeError:
              #this is thrown if a None is passed in for 'arg'
              return None

      mgmtip=args.mgmtip
      region=args.region
      username=args.username
      password=args.password
      masterfolder="./master"
      classfolder="./LABS"
      copy(masterfolder,classfolder)
      buildmain(mgmtip)
      os.system("cd LABS && terraform init")
      os.system("cd LABS && terraform apply -auto-approve")
main()
