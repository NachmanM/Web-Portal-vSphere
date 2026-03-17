import asyncio
import asyncpg
import os
from datetime import datetime, timezone
from .list_vms import fetch_all_vms_from_vcenter
from .list_vms import fetch_all_templates
async def sync_vcenter_to_db():
    print(f"[{datetime.now(timezone.utc)}] Starting vCenter inventory sync...")
    
    # 1. Fetch live inventory from vCenter
    vc_host = "10.190.20.10"
    vc_user = "administrator@vsphere.local"
    vc_pwd = os.getenv("VCENTER_PWD")
    
    # Run the blocking vCenter call in a separate thread to avoid freezing FastAPI
    live_vms = await asyncio.to_thread(fetch_all_vms_from_vcenter, vc_host, vc_user, vc_pwd)

    if not live_vms:
        print("Warning: No VMs retrieved from vCenter. Aborting sync to prevent accidental database wipe.")
        return

    # Extract just the IDs to find which ones to delete later
    live_vm_moids = [vm['vm_moid'] for vm in live_vms]

    # 2. Connect to PostgreSQL
    conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
    
    try:
        async with conn.transaction():
            # 3. UPSERT the live VMs
            for vm in live_vms:
                await conn.execute("""
                    INSERT INTO terraform_remote_state.vcenter_inventory_cache (vm_moid, vm_name, folder_name, power_state, portgroups, last_synced)
                    VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)
                    ON CONFLICT (vm_moid) DO UPDATE 
                    SET vm_name = EXCLUDED.vm_name,
                        folder_name = EXCLUDED.folder_name,
                        power_state = EXCLUDED.power_state,
                        last_synced = CURRENT_TIMESTAMP,
                        portgroups = EXCLUDED.portgroups;
                """, vm['vm_moid'], vm['name'], vm['folder'], vm['power_state'], vm['portgroups'])

            # 4. DELETE stale VMs (VMs in the DB that are no longer in vCenter)
            await conn.execute("""
                DELETE FROM vcenter_inventory_cache 
                WHERE vm_moid != ALL($1::varchar[])
            """, live_vm_moids)
            
            all_templates = await asyncio.to_thread(fetch_all_templates)
            for template in all_templates:
                await conn.execute("""
                    INSERT INTO terraform_remote_state.vcenter_templates (template, last_synced)
                    VALUES ($1, CURRENT_TIMESTAMP)
                    ON CONFLICT (template) DO UPDATE 
                    SET template = EXCLUDED.template,
                    last_synced = CURRENT_TIMESTAMP;
                """, template)

            await conn.execute("""
                DELETE FROM terraform_remote_state.vcenter_templates
                WHERE template != ALL($1::varchar[])
                """, all_templates)
            
        print("vCenter inventory sync completed successfully.")
        
    except Exception as e:
        print(f"Database sync failed: {e}")
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(sync_vcenter_to_db())
