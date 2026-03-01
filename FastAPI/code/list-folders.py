import ssl
import os
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from dotenv import load_dotenv


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
   
    # Create a recursive view of all VirtualMachine objects starting from Root
    # This is the standard pattern to "find all X"
    container = content.viewManager.CreateContainerView(
        content.rootFolder,
        [vim.Folder],
        True
    )
   
    folders = []
    for folder in container.view:
        folder_name = folder.name
        folder_code = folder.name.upper().replace(" ", "_")
        clean_folder_name = folder_name.strip().lower()
        if folder_name not in ["vm", "host", "datastore", "network"]:
            folders.append({
                "name": folder_name,
                "code": folder_code
            })
 
    print(folders)
    container.Destroy()

finally:
    Disconnect(si)
