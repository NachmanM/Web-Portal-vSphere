import asyncio
import asyncpg
import subprocess
import os
from datetime import date


# Configuration
PG_PWD = os.getenv("PG_PWD")
DB_CONFIG = {
    "user": "admin",
    "password": f"{PG_PWD}",
    "database": "postgres",
    "host": "postgres"
}
TF_DIR = "/FastAPI/Terraform"

async def run_terraform_destroy(workspace_uuid, full_delete=False):
    try:
        # 1. Switch to the correct workspace
        subprocess.run(["terraform", f"-chdir={TF_DIR}", "workspace", "select", workspace_uuid], check=True)
        
        # 2. Execute Destroy
        # Use -auto-approve for automation
        cmd = ["terraform", f"-chdir={TF_DIR}", "destroy", "-auto-approve", "-no-color", f"-var-file=../postgres-scripts/dummy.tfvars"]
        subprocess.run(cmd, check=True)
        
        if full_delete:
            # 3. Switch back to default to delete the workspace
            subprocess.run(["terraform", f"-chdir={TF_DIR}", "workspace", "select", "default"], check=True)
            subprocess.run(["terraform", f"-chdir={TF_DIR}", "workspace", "delete", workspace_uuid], check=True)
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"Terraform error for {workspace_uuid}: {e}")
        return False

async def daily_cleanup():
    conn = await asyncpg.connect(user='admin', password=PG_PWD, database='postgres', host='postgres')
    today = date.today()
    
    try:
        # Find VMs marked for deletion today or earlier that are not yet deleted
        # Note: 'Tim' is the owner associated with these deployments
        query = """
            SELECT state_key FROM terraform_remote_state.state_metadata 
            WHERE deletion_date <= $1 AND status != 'deleted'
        """
        records = await conn.fetch(query, today)
        
        for record in records:
            uuid = record['state_key']
            print(f"Starting deletion for workspace: {uuid}")
            
            success = await run_terraform_destroy(uuid, full_delete=True)
            
            if success:
                # Update status in DB or delete the metadata record
                await conn.execute(
                    "UPDATE terraform_remote_state.state_metadata SET status = 'deleted' WHERE state_key = $1", 
                    uuid
                )
                print(f"Successfully cleaned up {uuid}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(daily_cleanup())