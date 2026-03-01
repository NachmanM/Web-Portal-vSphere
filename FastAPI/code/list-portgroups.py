import ssl
import os
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from dotenv import load_dotenv


VCENTER_PWD = os.getenv("VCENTER_PWD")

context = ssl._create_unverified_context()

si = SmartConnect(
    host="10.190.20.10",
    user="administrator@vsphere.local",
    pwd=f"{VCENTER_PWD}",
    sslContext=context
)
target_host_name = "10.190.20.12" 
try:
    content = si.RetrieveContent()

    # 1. Utilize the SearchIndex to locate the specific HostSystem object directly
    host = content.searchIndex.FindByDnsName(
        datacenter=None,          # Set to a vim.Datacenter object to restrict the search scope, or None for global
        dnsName=target_host_name, 
        vmSearch=False            # Must be False to search for HostSystem objects instead of VirtualMachines
    )

    portgroups = []

    # 3. Traverse the network configuration tree for the isolated host
    if host.config and host.config.network and host.config.network.portgroup:
        for pg in host.config.network.portgroup:
            pg_name = pg.spec.name
            vlan = pg.spec.vlanId

            # I use pg_name as the code to pass it terraform
            portgroups.append(
                {
                    "name": f"VLAN {vlan} - {pg_name}",
                    "code": pg_name
                }
            )
    print(portgroups)

finally:
    Disconnect(si)