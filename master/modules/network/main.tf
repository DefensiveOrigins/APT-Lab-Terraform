resource "azurerm_virtual_network" "main" {
  name                = "${var.prefix}-network"
  address_space       = ["10.10.0.0/16"]
  location            = "${var.location}"
  resource_group_name = "${var.resource_group_name
}"
  dns_servers         = ["10.10.98.10", "1.1.1.1"]
}

resource "azurerm_subnet" "domain" {
  name                 = "domainNet"
  resource_group_name  = "${var.resource_group_name}"
  virtual_network_name = "${azurerm_virtual_network.main.name}"
  address_prefix       = "10.10.98.0/24"
}
