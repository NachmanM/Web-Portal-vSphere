output "ip" {
  value       = module.vm.ip
  description = "description"
}

output "uuid" {
  value       = module.vm.uuid
  description = "The real UUID of the VM"
}

output "moid" {
  value       = module.vm.moid
  description = "Managed object uuid"
}