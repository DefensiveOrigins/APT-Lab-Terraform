import urllib,json, subprocess, os, errno, shutil, argparse, configparser, csv
from requests import get

region="centralus"

subscription_id = ""
client_id       = ""
client_secret   = ""
tenant_id       = ""

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
    # The "feature" block is required for AzureRM provider 2.x. 
    # If you're using version 1.x, the "features" block is not allowed.
    version = "1.27.0"

    subscription_id = "subid"
    client_id       = "clid"
    client_secret   = "clse"
    tenant_id       = "tenid"
}
locals {
  resource_group_name   = "class-resources"
  master_admin_username ="itadmin"
  master_admin_password ="APTClass!"
  master_domain         ="labs.local"
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
    direction                       = "Inbound"
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
    direction                       = "Inbound"
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
    direction                       = "Outbound"
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
        metavar='input_mgmt', dest='mgmtip', type=str, nargs='+', required=True)
    args=parser.parse_args()
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
    masterfolder="./master"
    classfolder="./LABS"
    copy(masterfolder,classfolder)
    buildmain(mgmtip)
    os.system("cd LABS && terraform init")
    os.system("cd LABS && terraform apply -auto-approve")
main()
