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

    container = content.viewManager.CreateContainerView(
        content.rooFolder,
        [vim.VirtulMachine],
        True
    )

    templates = []
    for vm in container.view:
        if vm.config.template:
            templates.append(
                {
                    "name": vm.config.template,
                    "code": vm.config.template.upper().replace(" ", "_")
                }
            )
    container.Destroy()

finally:
    Disconnect(si)
