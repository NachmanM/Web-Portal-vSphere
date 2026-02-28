terraform {
  required_version = "~> 1.14.0"
  required_providers {
    vsphere = {
      source  = "hashicorp/vsphere"
      version = "2.12.0"
    }
  }
}

provider "vsphere" {
  user           = "administrator@vsphere.local"
  password       = var.VCENTER_PWD
  vsphere_server = "10.190.20.10"

  allow_unverified_ssl = true
}