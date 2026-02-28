module "vm" {
  source    = "./modules/vm"
  dc        = var.DC_name
  vmrpid    = data.vsphere_host.ESXi.resource_pool_id #Works with ESXi/Resources
  vmfolder  = "Nachman-Testing"
  datastore = "datastore1 (2)" #You can use datastore variable instead
  vmtemp    = "Ubuntu-25.04-Template"
  instances = 2
  vmname    = var.vm_name
  network ={
    "Jumpbox (VLAN-30)" = ["", ""]
  }
}