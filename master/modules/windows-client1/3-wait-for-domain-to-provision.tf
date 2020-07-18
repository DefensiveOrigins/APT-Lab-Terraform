resource "null_resource" "wait-for-domain-to-provision" {
  provisioner "local-exec" {
    command = "sleep 1020"
  }

  depends_on = [azurerm_virtual_machine.client]
}
