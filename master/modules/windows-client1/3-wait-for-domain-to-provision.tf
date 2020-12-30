resource "time_sleep" "wait-for-domain-to-provision" {
  depends_on = [azurerm_virtual_machine.client]

  create_duration = "1020s"
}

