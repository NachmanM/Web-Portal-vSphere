data "vsphere_datacenter" "dc" {
  name = var.DC_name
}

data "vsphere_host" "ESXi" {
  name          = var.esxi_host
  datacenter_id = data.vsphere_datacenter.dc.id
}