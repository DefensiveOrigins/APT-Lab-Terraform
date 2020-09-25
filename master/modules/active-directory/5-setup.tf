locals {
script = <<EOF
Invoke-Expression "$env:windir\system32\cscript.exe $env:windir\system32\slmgr.vbs /skms kms.core.windows.net:1688"
Invoke-Expression "$env:windir\system32\cscript.exe $env:windir\system32\slmgr.vbs /ato"
$password = ConvertTo-SecureString "APTClass!" -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential ("LABS\itadmin", $password)
$LocalTempDir = $env:TEMP; $ChromeInstaller = "ChromeSetup.exe"; (new-object    System.Net.WebClient).DownloadFile('https://dl.google.com/tag/s/appguid%3D%7B8A69D345-D564-463C-AFF1-A69D9E530F96%7D%26iid%3D%7B63FEF3AA-F182-26E9-2FB9-BD1031843FE2%7D%26lang%3Den%26browser%3D4%26usagestats%3D0%26appname%3DGoogle%2520Chrome%26needsadmin%3Dprefers%26ap%3Dx64-stable-statsdef_1%26installdataindex%3Dempty/update2/installers/ChromeSetup.exe', "$LocalTempDir\$ChromeInstaller"); & "$LocalTempDir\$ChromeInstaller" /silent /install; $Process2Monitor =  "ChromeInstaller"; Do { $ProcessesFound = Get-Process | ?{$Process2Monitor -contains $_.Name} | Select-Object -ExpandProperty Name; If ($ProcessesFound) { "Still running: $($ProcessesFound -join ', ')" | Write-Host; Start-Sleep -Seconds 2 } else { rm "$LocalTempDir\$ChromeInstaller" -ErrorAction SilentlyContinue -Verbose } } Until (!$ProcessesFound)
Invoke-WebRequest -Uri "https://the.earth.li/~sgtatham/putty/latest/w64/putty.exe" -OutFile "C:\Users\Public\Desktop\Putty.exe"
function Disable-ieESC {
    $AdminKey = "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A7-37EF-4b3f-8CFC-4F3A74704073}"
    $UserKey = "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A8-37EF-4b3f-8CFC-4F3A74704073}"
    Set-ItemProperty -Path $AdminKey -Name "IsInstalled" -Value 0
    Set-ItemProperty -Path $UserKey -Name "IsInstalled" -Value 0
    Write-Host "IE Enhanced Security Configuration (ESC) has been disabled." -ForegroundColor Green
}
Disable-ieESC
Set-Service -Name "FDResPub" -StartupType Automatic
Set-Service -Name "Dnscache" -StartupType Automatic
Set-Service -Name "SSDPSRV" -StartupType Automatic
Set-Service -Name "upnphost" -StartupType Automatic
Get-Service -DisplayName "Function Discovery Resource Publication" | Start-Service
Get-Service -DisplayName "DNS Client" | Start-Service
Get-Service -DisplayName "SSDP Discovery" | Start-Service
Get-Service -DisplayName "UPnP Device Host" | Start-Service
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
(Get-WmiObject -class Win32_TSGeneralSetting -Namespace root\cimv2\terminalservices -ComputerName localhost -Filter "TerminalName='RDP-tcp'").SetUserAuthenticationRequired(0)
$RDPUsers ="Net localgroup “Remote Desktop Users” /add “LABS\Domain Users"
Invoke-command -computername localhost -scriptblock {$RDPUsers} -Credential $Cred
C:/LABS/scripts/ad-users-create-script.ps1 ${var.admin_password} ${var.admin_username}
C:/LABS/scripts/shareLabs.ps1
Remove-WindowsFeature Windows-Defender, Windows-Defender-GUI
ping 1.1.1.1
Restart-Computer
EOF
  settings_windows = {
    script   = "${compact(concat(split("\n", local.script)))}"
  }
}

data "azurerm_resource_group" "main" {
  name = "${var.resource_group_name}"
}

data "azurerm_virtual_machine" "main" {
  name                = "${azurerm_virtual_machine.domain-controller.name}"
  resource_group_name = "${data.azurerm_resource_group.main.name}"
}

resource "azurerm_virtual_machine_extension" "windows" {
  name                       = "${azurerm_virtual_machine.domain-controller.name}-run-command"
  location                   = "${data.azurerm_resource_group.main.location}"
  resource_group_name        = "${data.azurerm_resource_group.main.name}"
  virtual_machine_name       = "${data.azurerm_virtual_machine.main.name}"
  publisher                  = "Microsoft.CPlat.Core"
  type                       = "RunCommandWindows"
  type_handler_version       = "1.1"
  auto_upgrade_minor_version = true
  settings                   = "${jsonencode(local.settings_windows)}"

depends_on = [null_resource.wait-for-dc]
}


