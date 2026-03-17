import ssl
import os
import asyncio
import asyncpg
# from pyVim.connect import SmartConnect, Disconnect
# from pyVmomi import vim
# from dotenv import load_dotenv


# VCENTER_PWD = os.getenv("VCENTER_PWD")
# # 1. BYPASS SSL (Common in internal labs, strictly unsafe for prod)
# context = ssl._create_unverified_context()

# # 2. CONNECT
# # Connects to the API and returns the ServiceInstance (SI)
# si = SmartConnect(
#     host="10.190.20.10",
#     user="administrator@vsphere.local",
#     pwd=f"{VCENTER_PWD}",
#     sslContext=context
# )

# try:
#     # 3. GET CONTENT & VIEW MANAGER
#     content = si.RetrieveContent()

#     container = content.viewManager.CreateContainerView(
#         content.rootFolder,
#         [vim.VirtualMachine],
#         True
#     )

#     templates = []
#     for vm in container.view:
#         if vm.config.template:
#             templates.append(
#                 {
#                     "name": vm.config.name,
#                     "code": vm.config.name.upper().replace(" ", "_")
#                 }
#             )
#     print(templates)
#     container.Destroy()

# finally:
#     Disconnect(si)

async def list_templates():
    conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
    try:
        row = await conn.fetch(
            "SELECT template "
            "FROM terraform_remote_state.vcenter_templates "
        )
        clean_list = []
        for r in row:
            clean_list.append(r['template'])
        unique_list = set(clean_list)
        resp_list = []
        for u in unique_list:
            resp_list.append({
                "name": u,
                "code": u
            })
        print(resp_list)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

asyncio.run(list_templates())