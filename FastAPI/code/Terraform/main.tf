module "vm" {
  source    = "./modules/vm"
  dc        = var.DC_name
  vmrpid    = data.vsphere_host.ESXi.resource_pool_id #Works with ESXi/Resources
  vmfolder  = var.folder
  datastore = "datastore1 (2)" #You can use datastore variable instead
  vmtemp    = var.template

  instances        = 1
  vmname           = var.vm_name
  is_windows_image = var.is_windows_image

  ram_size     = var.ram_size
  cpu_number   = var.cpu_number
  disk_size_gb = var.disk_size_gb

  network = {
    (var.portgroup) = [""]
  }
  wait_for_guest_ip_timeout = 5
}