from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import os

def fetch_all_vms_from_vcenter(vcenter_host, vcenter_user, vcenter_password):
    context = ssl._create_unverified_context()
    
    try:
        service_instance = SmartConnect(
            host=vcenter_host, 
            user=vcenter_user, 
            pwd=vcenter_password,
            sslContext=context
        )
    except Exception as e:
        print(f"Connection to vCenter failed: {e}")
        return []

    try:
        content = service_instance.RetrieveContent()
        
        # Create a ContainerView configured to search recursively for VirtualMachines
        container_view = content.viewManager.CreateContainerView(
            content.rootFolder, 
            [vim.VirtualMachine], 
            True
        )
        
        vm_inventory = []
        
        for vm in container_view.view:
            try:
                # Extract immutable managed object ID (moId)
                vm_moid = vm._moId 
                
                # Extract basic properties
                vm_name = vm.name
                power_state = vm.runtime.powerState # Returns 'poweredOn', 'poweredOff', or 'suspended'
                
                # In vSphere, a VM's immediate parent is always a vim.Folder object
                folder_name = vm.parent.name if vm.parent else "Unknown"

                networks = []
                for net in vm.network:
                    networks.append(net.name)
                
                vm_inventory.append({
                    "vm_moid": vm_moid,
                    "name": vm_name,
                    "folder": folder_name,
                    "power_state": power_state,
                    "portgroups": networks
                })
                
            except vim.fault.NoPermission:
                print(f"Permission denied to read properties for VM ID: {vm._moId}")
                continue
            except Exception as e:
                print(f"Failed to process VM ID {vm._moId}: {e}")
                continue
                
        # Destroy the view to free memory on the vCenter server immediately
        container_view.Destroy()
        
        return vm_inventory
    finally:
        Disconnect(service_instance)

def fetch_all_templates():
    VCENTER_PWD = os.getenv("VCENTER_PWD")
    # 1. BYPASS SSL (Common in internal labs, strictly unsafe for prod)
    context = ssl._create_unverified_context()

    # 2. CONNECT
    # Connects to the API and returns the ServiceInstance (SI)
    si = SmartConnect(
        host="10.190.20.10",
        user="administrator@vsphere.local",
        pwd=f"{VCENTER_PWD}",
        sslContext=context
    )

    try:
        # 3. GET CONTENT & VIEW MANAGER
        content = si.RetrieveContent()

        container = content.viewManager.CreateContainerView(
            content.rootFolder,
            [vim.VirtualMachine],
            True
        )

        templates = []
        for vm in container.view:
            if vm.config.template:
                templates.append(vm.config.name)
        container.Destroy()
        return templates
        

    finally:
        Disconnect(si)

# --- Execution Example ---
if __name__ == "__main__":
    import os
    VCENTER_HOST = "10.190.20.10"
    VCENTER_USER = "administrator@vsphere.local"
    VCENTER_PASSWORD = os.getenv("VCENTER_PWD")

    vms = fetch_all_vms_from_vcenter(VCENTER_HOST, VCENTER_USER, VCENTER_PASSWORD)
    print(f"Retrieved {len(vms)} VMs from vCenter.")
    
    # Print a sample of the output
    for vm in vms[:5]:
        print(vm)

    for t in fetch_all_templates():
        print(t)