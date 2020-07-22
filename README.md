


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

