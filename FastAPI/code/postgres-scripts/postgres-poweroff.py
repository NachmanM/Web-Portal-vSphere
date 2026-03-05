import asyncio
import asyncpg
import ssl
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import os

VCENTER_HOST = "10.190.20.10"
VCENTER_USER = "administrator@vsphere.local"
VCENTER_PWD  = os.getenv("VCENTER_PWD")
PG_CONN_STR  = os.getenv("PG_CONN_STR")

def refresh_vm_obj(content, vm):
    """
    Refreshes the properties of a specific VM object 
    by re-fetching it from the PropertyCollector.
    """
    property_collector = content.propertyCollector
    obj_spec = vim.PropertyCollector.ObjectSpec(obj=vm)
    prop_spec = vim.PropertyCollector.PropertySpec(type=vim.VirtualMachine, all=True)
    spec = vim.PropertyCollector.FilterSpec(objectSet=[obj_spec], propSet=[prop_spec])
    
    # This call forces the script to wait for the latest update from the server
    return property_collector.RetrieveProperties(specSet=[spec])

async def shutdown_by_real_uuid():
    conn = await asyncpg.connect(PG_CONN_STR)
    query = """
        SELECT vcenter_uuid, state_key 
        FROM terraform_remote_state.state_metadata 
        WHERE shutdown_date <= CURRENT_DATE 
        AND status = 'active'
        AND vcenter_uuid IS NOT NULL;
    """
    rows = await conn.fetch(query)
    
    if not rows:
        await conn.close()
        return


    si = SmartConnect(host=VCENTER_HOST, user=VCENTER_USER, pwd=VCENTER_PWD, sslContext=ssl._create_unverified_context())
    content = si.RetrieveContent()
    try:
        
        for row in rows:
            target_moid = row['vcenter_uuid']
            print(target_moid)
            
            vm = vim.VirtualMachine(target_moid, si._stub)

            if vm:
                print(f"Host Connection State: {vm.runtime.host.runtime.connectionState}")
                print(vm.runtime.powerState)
                if vm.summary.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                    vm.PowerOffVM_Task() 
                    print("Found a row")
                    await conn.execute(
                        "UPDATE terraform_remote_state.state_metadata SET status = 'powered_off' WHERE vcenter_uuid = $1",
                        target_moid
                    )
                    print("Updated the VM to powered_off in the DB")
            else:
                print(f"VM {target_moid} not found in vCenter.")

    finally:
        Disconnect(si)
        print("Disconnecting")
        await conn.close()

if __name__ == "__main__":
    asyncio.run(shutdown_by_real_uuid())