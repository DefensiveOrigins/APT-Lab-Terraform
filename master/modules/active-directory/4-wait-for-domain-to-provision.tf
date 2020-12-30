resource "time_sleep" "wait-for-dc" {
  depends_on = [azurerm_virtual_machine_extension.create-active-directory-forest]

  create_duration = "300s"
}

