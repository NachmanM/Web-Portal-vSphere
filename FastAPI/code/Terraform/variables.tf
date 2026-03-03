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

variable "ram_size" {
  type        = number
  description = "RAM size in megabytes"
  default     = 8192
}

variable "cpu_number" {
  description = "number of CPU cores"
  default     = 3
  type        = number
}

variable "disk_size_gb" {
  description = "List of disk sizes to override template disk size"
  type        = list(any)
  default     = null
}

