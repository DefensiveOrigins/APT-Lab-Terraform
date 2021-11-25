module "run_command" {
  source               = "github.com/oerlex/terraform-azurerm-vm-run-command.git"
  resource_group_name  = var.resource_group_name
  virtual_machine_name  = azurerm_virtual_machine.linux.name
  os_type              = "linux"
  depends_on = [azurerm_virtual_machine.linux]

  script = <<EOF
apt-get update
apt-get install -y git python3-pip python3.8 p7zip-full 
python3.6 -m pip install virtualenv
apt-get install -y python3-venv
chmod 777 /opt
cd /opt/
wget https://github.com/DefensiveOrigins/APT-Lab-Terraform-Linux/raw/master/linuxtools.7z
7z x linuxtools.7z
mkdir SilentTrinity
mkdir CrackMapExec
mv st SilentTrinity/
mv cme* CrackMapExec/
rm linuxtools.7z
git clone https://github.com/Cyb3rWard0g/HELK.git
cd HELK/docker
./helk_install.sh -p hunting -i 10.10.98.20 -b 'helk-kibana-analysis-alert'
cd /opt/
git clone https://github.com/lgandx/Responder.git
git clone https://github.com/SecureAuthCorp/impacket.git
cd impacket
python3.6 -m venv env
EOF
}
