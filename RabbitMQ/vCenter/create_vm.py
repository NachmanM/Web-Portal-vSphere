import json
import subprocess
import os
import asyncio
import asyncpg
from datetime import datetime
from pydantic import BaseModel
from logger_config import setup_logger

logger = setup_logger("InfraService")

class VMCreation(BaseModel):
    owner: str
    vm_name: str
    folder: str
    template: str
    portgroup: str
    is_windows_image: str
    ram_size: int
    cpu_number: int
    disk_size_gb: list
    shutdown_date: datetime
    deletion_date: datetime
    transaction_uuid: str

async def run_db_execute(query: str, *args):
    """Executes a standalone database query."""
    conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
    try:
        return await conn.execute(query, *args)
    finally:
        await conn.close()

async def insert_db_record(payload: VMCreation, random_uuid: str):
    """Initializes the database records before provisioning."""
    conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
    try:
        query_metadata = """
        INSERT INTO terraform_remote_state.state_metadata (
            state_key, owner, folder, portgroup, template_used, 
            cpu_cores, ram_mb, disk_gb, shutdown_date, deletion_date, vcenter_uuid, status
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 'provisioning')
        """
        await conn.execute(
            query_metadata, 
            random_uuid, payload.owner, payload.folder, payload.portgroup,
            payload.template, payload.cpu_number, payload.ram_size,
            int(payload.disk_size_gb[0]), payload.shutdown_date,
            payload.deletion_date, f"pending-{random_uuid}"
        )
        
        await conn.execute(
            "INSERT INTO terraform_remote_state.vcenter_inventory_cache "
            "(vm_moid, vm_name, folder_name, power_state) "
            "VALUES ($1, $2, $3, 'provisioning');",
            f"pending-{random_uuid}", payload.vm_name, payload.folder
        )
    finally:
        await conn.close()

def execute_vcenter_provisioning(payload: VMCreation):
    """Orchestrates Terraform commands and database updates."""
    random_uuid = payload.transaction_uuid
    try:
        # 1. Reset the local workspace cache to 'default' to prevent interactive ghost-state prompts
        env_file_path = os.path.join("Terraform", ".terraform", "environment")
        if os.path.exists(env_file_path):
            with open(env_file_path, "w") as f:
                f.write("default")
        logger.info(f"[{random_uuid}] Initializing Terraform workspace.")
        subprocess.run(["terraform", "-chdir=Terraform", "init", "-no-color"], capture_output=True, text=True, check=True)
        subprocess.run(["terraform", "-chdir=Terraform/", "workspace", "new", f"{random_uuid}", "-no-color"], 
                       capture_output=True, text=True, check=True)
    
        logger.info(f"[{random_uuid}] Inserting initial database records.")
        asyncio.run(insert_db_record(payload, random_uuid))

        disk_size_json = json.dumps(payload.disk_size_gb)
        cmd_apply = [
            "terraform", "-chdir=Terraform", "apply", "-no-color",
            f"-var=vm_name={payload.vm_name}",
            f"-var=folder={payload.folder}",
            f"-var=template={payload.template}",
            f"-var=portgroup={payload.portgroup}",
            f"-var=is_windows_image={payload.is_windows_image}",
            f"-var=ram_size={payload.ram_size}",
            f"-var=cpu_number={payload.cpu_number}",
            f"-var=disk_size_gb={disk_size_json}",
            "-auto-approve"
        ]
        
        logger.info(f"[{random_uuid}] Executing Terraform apply.")
        apply_result = subprocess.run(cmd_apply, capture_output=True, text=True, check=True)
        logger.debug(f"[{random_uuid}] Terraform Output: {apply_result.stdout}")

        cmd_out = ["terraform", "-chdir=Terraform", "output", "-json", "moid"]
        output_result = subprocess.run(cmd_out, capture_output=True, text=True, check=True)
        uuid_list = json.loads(output_result.stdout)
        real_uuid = uuid_list[0] if uuid_list else None

        if real_uuid:
            logger.info(f"[{random_uuid}] Provisioning complete. Updating database with MOID: {real_uuid}")
            asyncio.run(run_db_execute(
                "UPDATE terraform_remote_state.state_metadata SET vcenter_uuid = $1, status = 'active' WHERE state_key = $2",
                real_uuid, random_uuid
            ))
            asyncio.run(run_db_execute(
                "UPDATE terraform_remote_state.vcenter_inventory_cache SET vm_moid = $1, power_state = 'poweredOn' WHERE vm_moid = $2",
                real_uuid, f"pending-{random_uuid}"
            ))

        return {"status": "success", "created": f"{apply_result.stdout}", "real_moid": real_uuid}

    except subprocess.CalledProcessError as e:
        error_output = e.stderr if e.stderr else e.stdout
        logger.error(f"[{random_uuid}] Terraform command failed. STDOUT: {e.stdout} | STDERR: {e.stderr}")
        
        logger.info(f"[{random_uuid}] Cleaning up pending database records due to failure.")
        asyncio.run(run_db_execute("DELETE FROM terraform_remote_state.vcenter_inventory_cache WHERE vm_moid = $1", f"pending-{random_uuid}"))
        asyncio.run(run_db_execute("DELETE FROM terraform_remote_state.state_metadata WHERE state_key = $1", random_uuid))
        
        return {"detail": f"Terraform command failed: Error: {error_output}"}
        
    except Exception as e:
        logger.critical(f"[{random_uuid}] Internal System Error during provisioning.", exc_info=True)
        return {"status": "failed", "message": "Internal System Error", "command_result": str(e)}