variable "DC_name" {
  type        = string
  default     = "MTP-LAB"
  description = "Name of the datacenter"
}

variable "VCENTER_PWD" {
  type      = string
  sensitive = true
}

variable "esxi_host" {
  type    = string
  default = "10.190.20.12"
}

variable "vm_name" {
  type = string
}

variable "folder" {
  type = string
}

variable "template" {
  type = string
}

variable "is_windows_image" {
  type = bool
}

variable "portgroup" {
  type = string
}