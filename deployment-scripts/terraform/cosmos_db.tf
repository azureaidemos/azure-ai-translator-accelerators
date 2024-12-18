# Generate a random complex password
resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}
resource "azurerm_postgresql_flexible_server" "translator_db" {
  name                = "${local.name_prefix}-transaltor-db-${random_string.unique.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  # Administrator details
  administrator_login    = var.postgres_administrator_login
  administrator_password = random_password.db_password.result # Use the generated password

  # Serverless Configuration
  sku_name   = "B_Standard_B1ms" # Serverless SKU
  storage_mb = 32768             # 32 GB minimum storage
  version    = "16"              # PostgreSQL version

  # Public Access Configuration
  public_network_access_enabled = true # Enable public access
  zone                          = "2"

  # Backup Retention
  backup_retention_days = 35
  auto_grow_enabled     = true
  timeouts {
    create = "2h"
    update = "2h"
  }
}

# Create a PostgreSQL Database
resource "azurerm_postgresql_flexible_server_database" "citus_db" {
  name      = var.postgres_db_name
  server_id = azurerm_postgresql_flexible_server.translator_db.id
  collation = "en_US.utf8"
  charset   = "UTF8"

  # prevent the possibility of accidental data loss
  #   lifecycle {
  #     prevent_destroy = true
  #   }
}

# # Firewall Rule to allow public IP access
resource "azurerm_postgresql_flexible_server_firewall_rule" "example" {
  name             = "allow-public-ip"
  start_ip_address = "0.0.0.0" # Allow all IPs (not recommended for production)
  end_ip_address   = "255.255.255.255"
  server_id        = azurerm_postgresql_flexible_server.translator_db.id
}


# Output connection details
output "postgres_host" {
  value = azurerm_postgresql_flexible_server.translator_db.fqdn
}

output "postgres_port" {
  value = 5432
}

output "postgres_database" {
  value = azurerm_postgresql_flexible_server_database.citus_db.name
}

output "postgres_username" {
  value = var.postgres_administrator_login
}

output "postgres_password" {
  value     = random_password.db_password.result
  sensitive = true
}

# Null resource to run the SQL script using psql
# resource "null_resource" "run_sql_script" {
#   depends_on = [azurerm_postgresql_flexible_server_database.citus_db]

#   provisioner "local-exec" {
#     command = <<EOT
#       PGPASSWORD='${random_password.db_password.result}' psql \
#       -h ${azurerm_postgresql_flexible_server.translator_db.fqdn} \
#       -p 5432 \
#       -d ${azurerm_postgresql_flexible_server_database.citus_db.name} \
#       -U ${var.postgres_administrator_login} \
#       -f db.sql
#     EOT

#     interpreter = ["bash", "-c"]
#   }
# }
