resource "null_resource" "wait-for-dc" {
  provisioner "local-exec" {
    command = "sleep 300"
  }
  depends_on = [azurerm_virtual_machine_extension.create-active-directory-forest]
}
