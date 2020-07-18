resource "azurerm_virtual_machine_extension" "join-domain" {
  name                 = "${azurerm_virtual_machine.client.name}"
  location             = "${azurerm_virtual_machine.client.location}"
  resource_group_name  = "${var.resource_group_name}"
  virtual_machine_name = "${azurerm_virtual_machine.client.name}"
  publisher            = "Microsoft.Compute"
  type                 = "JsonADDomainExtension"
  type_handler_version = "1.3"

  settings = <<SETTINGS
    {
        "Name": "${var.active_directory_domain}",
        "User": "${var.active_directory_username}@${var.active_directory_domain}",
        "OUPath": "",
        "Restart": "true",
        "Options": "3"
    }
SETTINGS

  protected_settings = <<PROTECTED_SETTINGS
    {
        "Password": "${var.active_directory_password}"
    }
PROTECTED_SETTINGS
depends_on = [null_resource.wait-for-domain-to-provision]
}
