import ssl
import os
import sys
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl

# Parses the last argument as the vCenter Managed Object ID
moid = sys.argv[-1]

def _get_folder_path(vm):
    """Traverses the parent hierarchy to construct the logical folder path."""
    folder = vm.parent
    path = []
    while folder is not None and isinstance(folder, vim.Folder):
        if folder.name == "vm" and isinstance(folder.parent, vim.Datacenter):
            break
        path.append(folder.name)
        folder = folder.parent
    path.reverse()
    return "/" + "/".join(path) if path else "/"

def get_vm_info():
    
    
    try:
        VCENTER_PWD = os.getenv("VCENTER_PWD")
        context = ssl._create_unverified_context()
        si = SmartConnect(
            host="10.190.20.10",
            user="administrator@vsphere.local",
            pwd=f"{VCENTER_PWD}",
            sslContext=context
            )
        
        
        vm = vim.VirtualMachine(moid, stub=si._stub)
        
        # 3. Trigger API call to verify existence
        name = vm.summary.config.name
        
        # 4. Extract total disk capacity and individual disks
        total_disk_gb = 0
        disks = []
        if vm.config and vm.config.hardware and vm.config.hardware.device:
            for device in vm.config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualDisk):
                    capacity_gb = device.capacityInKB / (1024**2)
                    total_disk_gb += capacity_gb
                    disks.append({
                        "label": device.deviceInfo.label,
                        "capacity_gb": round(capacity_gb, 2)
                    })

        # 5. Extract network portgroups and attempt VLAN extraction for vDS
        networks = []
        for network in vm.network:
            net_info = {"name": network.name}
            if isinstance(network, vim.dvs.DistributedVirtualPortgroup):
                try:
                    vlan_config = network.config.defaultPortConfig.vlan
                    if isinstance(vlan_config, vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec):
                        net_info["vlan"] = str(vlan_config.vlanId)
                    elif isinstance(vlan_config, vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec):
                        net_info["vlan"] = "Trunk"
                except AttributeError:
                    net_info["vlan"] = "Unknown"
            else:
                net_info["vlan"] = "Standard vSwitch"
            networks.append(net_info)

        import json
        import sys

# ... inside your main logic or function ...

        vm_data = {
            "moid": moid,
            "name": name,
            "os": vm.summary.config.guestFullName,
            "state": str(vm.runtime.powerState),  # Convert Enum to string for JSON
            "ram_gb": round(vm.summary.config.memorySizeMB / 1024, 2) if vm.summary.config.memorySizeMB else 0,
            "cpu_count": vm.summary.config.numCpu,
            "total_disk_gb": round(total_disk_gb, 2),
            "disks": disks,
            "networks": networks,
            "folder": _get_folder_path(vm),
            "ip_address": vm.guest.ipAddress,
            "host": vm.runtime.host.name if vm.runtime.host else "Unknown"
        }

        # The Critical Step: Print as a JSON string
        print(vm_data)
    except Exception as e:
        print(e)
    except vmodl.fault.ManagedObjectNotFound:
        return {"error": f"VirtualMachine with MOID '{moid}' not found."}
    except vim.fault.InvalidLogin:
        return {"error": "Invalid vCenter credentials."}
    except Exception as e:
        return {"error": f"Execution failed: {str(e)}"}
    
    finally:
        # 7. Ensure the session is terminated to prevent vCenter resource leaks
        if si:
            Disconnect(si)

if __name__ == '__main__':
    get_vm_info()