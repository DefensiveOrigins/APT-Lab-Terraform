# APT-Lab-Terraform
Purple Teaming Attack &amp; Hunt Lab - Terraform

THIS MUST BE RAN FROM A LINUX HOST WITH PYTHON 3.

Install AzureCLI
https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-apt?view=azure-cli-latest

Install Terraform
https://learn.hashicorp.com/terraform/getting-started/install.html

Create Token/Document
https://www.terraform.io/docs/providers/azurerm/guides/service_principal_client_secret.html


Edit LabBuilder.py and add in your Token info at the top of the file. You can also update the Region variable to desired region.

List of regions can be found here that offer the Bs-series we use in this lab environment.
https://azure.microsoft.com/en-us/global-infrastructure/services/?products=virtual-machines

Next lets build the working directory and deploy
git clone https://github.com/DefensiveOrigins/APT-Lab-Terraform.git

cd APT-Lab-Terraform

Next you will run the builder and deploy your systems. 
python .\LabBuilder.py -m YOURPUBLICIP

-m will accept a single IP Address or Subnet as input
