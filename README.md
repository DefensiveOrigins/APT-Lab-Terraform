


![Defensive Origins](https://defensiveorigins.com/wp-content/uploads/2020/05/defensive-origins-header-6-1536x760.png)

# Applied Purple Teaming Threat Optics Lab - Azure TerraForm 
Purple Teaming Attack &amp; Hunt Lab - TerraForm

<!-- Start Document Outline -->

* [Background](#background)
* [Installation:](#installation)
	* [Install AzureCLI](#install-azurecli)
	* [Install TerraForm](#install-terraform)
* [Setup and Build](#setup-and-build)
	* [Create Token/Document](#create-tokendocument)
	* [Configure Regions](#configure-regions)
	* [Clone APT TerraForm Repository](#clone-apt-terraform-repository)
	* [Execute TerraForm build process](#execute-terraform-build-process)
	* [Source IP Filtering](#source-ip-filtering)

<!-- End Document Outline -->

---
## Background
Defensive Origins uses a highly verbose threat optics lab to isolate adversarial techniques to more easily attribute IOC (indicators of compromise).  These labs have routinely been time consuming to build and manage.  The platform included here automates much of the threat-optic lab environment built on the Azure cloud network.

## Installation:

This process requires Python3.

### Install AzureCLI
https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-apt?view=azure-cli-latest

### Install TerraForm
https://learn.hashicorp.com/terraform/getting-started/install.html

## Setup and Build

### Create Token/Document
* https://www.terraform.io/docs/providers/azurerm/guides/service_principal_client_secret.html
* Edit LabBuilder.py and add in your Token info at the top of the file. 

### Configure Regions
* You can also update the Region variable to desired region. This is updated LabBuilder.py.
* List of regions can be found here that offer the Bs-series we use in this lab environment.
* https://azure.microsoft.com/en-us/global-infrastructure/services/?products=virtual-machines

### Clone APT TerraForm Repository

```bash
git clone https://github.com/DefensiveOrigins/APT-Lab-Terraform.git
cd APT-Lab-Terraform
```

### Execute TerraForm build process
Run the builder and deploy your systems.

```bash
python .\LabBuilder.py -m YOURPUBLICIP
```
### Source IP Filtering
The -m flag will accept a single IP Address or Subnet as input. This adds the IP as a SRC IP address filter on the lab environment. 
```bash
-m [IP]
```

--- 

# Modules
The various components of this build process are defined below.

| Module          | Function                                 |
|-----------------|------------------------------------------|
| /master/modules | Various TerraForm modules                |
| LabBuilder.py   | Python script that uses TerraForm and AzureCLI to build the Applied Purple Teaming to specifications using the modules in /master/modules and additional resources. |
| labs.zip        | Additional resources to configure lab encironment. |


### Network

This module creates a Network with 2 x Subnets:
* Domain Controllers
* Domain Clients

This module shouldn't be used as-is in a Production Environment - where you'd probably have Network Security Rules configured - it's designed to be a simplified configuration for the purposes of this example.

| Module       | Function                |
|--------------|-------------------------|
| main.tf      | Setup Primary Network   |
| outputs.tf   | Grab and Set Network ID |
| variables.tf | TerraForm variables     |


### Active Directory
* This module is designed to quickly spin up an Active Directory Forest on a single node, this is by no means best practice and we'd highly recommend not using this approach in Production.
* This module was based on / heavily inspired by: https://github.com/bobalob/Terraform-AzureRM-Example/tree/winrm-https

| Module                            | Function                                 |
|-----------------------------------|------------------------------------------|
| 1-network-interface.tf            | Setup interface of Domain Controller     |
| 2-virtual-machine.tf              | Specify Domain Controller VM Attributes  |
| 3-provision-domain.tf             | Initial Domain Configuration             |
| 4-wait-for-domain-to-provision.tf | Quietly wait for Domain to finish provisioning |
| 5-setup.tf                        | Domain Controller Services and Software Configuration |
| variables.tf                      | TerraForm variables                      |
| files/FirstLogonCommands.xml      | Run first commands                       |
| files/winrm.ps1                   | Enable WinRM, grab Lab resources         |

### Linux / Helk 
* This module configures a Ubuntu image with the necessary tooling to be used as a hunters-SIEM (HELK)

| Module                 | Function                                 |
|------------------------|------------------------------------------|
| 1-network-interface.tf | Setup interface for Linux system         |
| 2-virtual-machine.tf   | Specify VM configuration for Linux System |
| 3-setup.tf             | Setup and configure software             |
| variables.tf           | TerraForm variables                      |

### Windows Client
* This module provisions a Windows Client which will be bound to the Active Directory Domain created in the other module.
* There's a few hacks in here as we have to wait for Active Directory to become available, but this takes advantage of the **azurerm_virtual_machine_extension** resource. It's worth noting that the keys in this resource are case sensitive.

| Module                            | Function                                 |
|-----------------------------------|------------------------------------------|
| 1-network-interface.tf            | Setup network interface for Windows client |
| 2-virtual-machine.tf              | Specify client VM configuration          |
| 3-wait-for-domain-to-provision.tf | Politely wait for the Domain to be provisioned |
| 4-join-domain.tf                  | Join Windows client to domain.           |
| 5-setup.tf                        | Procure and configure the various tools. |
| outputs.tf                        | Grab the associated VM IP.               |
| variables.tf                      | TerraForm varaibles                      |





## Hat-Tips and Acknowledgments
* https://github.com/bobalob/Terraform-AzureRM-Example/tree/winrm-https 
  * Gave us a head start on setting up the necessary configuration to use WinRM for deployment.
