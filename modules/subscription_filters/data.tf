locals {
  config = yamldecode(file(var.config_disk_path))
}
