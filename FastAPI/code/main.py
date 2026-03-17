from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os
import ast
import json
import asyncio
import asyncpg
from datetime import datetime
from sync_pg.sync_pg_lifecycle import lifespan




PG_PWD = os.getenv("PG_PWD")
app = FastAPI(lifespan=lifespan)

# CORS — allow local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AppsmithPayload(BaseModel):
    message: str

class PendingVMPayload(BaseModel):
    vm_name: str
    folder_name: str

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
    conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
    try:
        # The *args here unpacks the tuple back into individual arguments for the driver
        return await conn.execute(query, *args)
    finally:
        await conn.close()

@app.post('/vm')
def create_vm(payload: VMCreation):
    try:
        import uuid
        random_uuid = payload.transaction_uuid
        
        cmd = ["terraform", "-chdir=Terraform", "init"]
        init_result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        cmd = ["terraform", "-chdir=Terraform/", "workspace", "new", f"{random_uuid}"]
        workspace_result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
        async def insert_db_record():
            conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
            try:
                query = """
                INSERT INTO terraform_remote_state.state_metadata (
                    state_key, owner, folder, portgroup, template_used, 
                    cpu_cores, ram_mb, disk_gb, shutdown_date, deletion_date, vcenter_uuid, status
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 'provisioning'
                )
                """
            
                await conn.execute(
                    query, 
                    random_uuid,                    # Maps to $1 (State key is the generated UUID)
                    payload.owner,                  # Maps to $2 (Ensure 'owner' exists in your VMCreation model)
                    payload.folder,                 # Maps to $3
                    payload.portgroup,              # Maps to $4
                    payload.template,               # Maps to $5 (Matches your terraform var)
                    payload.cpu_number,             # Maps to $6 (Matches your terraform var)
                    payload.ram_size,               # Maps to $7 (Matches your terraform var)
                    int(payload.disk_size_gb[0]),   # Maps to $8 (Matches your terraform var)
                    payload.shutdown_date,          # Maps to $9 (Ensure this exists in your model)
                    payload.deletion_date,          # Maps to $10 (Ensure this exists in your model)
                    f"pending-{random_uuid}"        # Maps to $11
                )
                
                await conn.execute(
                    "INSERT INTO terraform_remote_state.vcenter_inventory_cache "
                    "(vm_moid, vm_name, folder_name, power_state) "
                    "VALUES ($1, $2, $3, 'provisioning');",
                    f"pending-{random_uuid}", payload.vm_name, payload.folder
                )
            finally:
                await conn.close()

        asyncio.run(insert_db_record())
        

        disk_size_gb = json.dumps(payload.disk_size_gb)
        cmd2 = ["terraform", "-chdir=Terraform", "apply", "-no-color",
                 f"-var=vm_name={payload.vm_name}",
                 f"-var=folder={payload.folder}",
                 f"-var=template={payload.template}",
                 f"-var=portgroup={payload.portgroup}",
                 f"-var=is_windows_image={payload.is_windows_image}",
                 f"-var=ram_size={payload.ram_size}",
                 f"-var=cpu_number={payload.cpu_number}",
                 f"-var=disk_size_gb={disk_size_gb}",
                  "-auto-approve"]
        
        apply_result = subprocess.run(cmd2, capture_output=True, text=True, check=True)

        cmd_output = ["terraform", "-chdir=Terraform", "output", "-json", "moid"]
        output_result = subprocess.run(cmd_output, capture_output=True, text=True, check=True)
        uuid_list = json.loads(output_result.stdout)
        real_uuid = uuid_list[0]
        if real_uuid:
            # 2. Save the MOID to the vcenter column
            asyncio.run(run_db_execute("UPDATE terraform_remote_state.state_metadata SET vcenter_uuid = $1 WHERE state_key = $2",
                    real_uuid, random_uuid))
            
            asyncio.run(run_db_execute("UPDATE terraform_remote_state.state_metadata SET status = 'active' WHERE vcenter_uuid = $1",
                    real_uuid))
                    
            asyncio.run(run_db_execute("UPDATE terraform_remote_state.vcenter_inventory_cache SET vm_moid = $1, power_state = 'poweredOn' WHERE vm_moid = $2",
                    real_uuid, f"pending-{random_uuid}"))

        return {"status": "success", "created": f"{apply_result.stdout}", "real_moid": real_uuid}
    except subprocess.CalledProcessError as e:
        # e.stderr contains the exact red text error generated by Terraform
        # e.stdout contains the standard output up until the point of failure
        error_output = e.stderr if e.stderr else e.stdout
        
        # Cleanup pending VM on terraform failure
        asyncio.run(run_db_execute("DELETE FROM terraform_remote_state.vcenter_inventory_cache WHERE vm_moid = $1", f"pending-{random_uuid}"))
        asyncio.run(run_db_execute("DELETE FROM terraform_remote_state.state_metadata WHERE state_key = $1", random_uuid))
        
        # FastAPI Example
        from fastapi import JSONResponse

        # Inside your route logic, when Terraform fails:
        return {"detail": f"Terraform command failed output: Error: {error_output}"}


    
    except Exception as e:
        # This acts as a fallback for database timeouts or Python syntax errors
        return {
            "status": "failed", 
            "message": "Internal System Error", 
            "command_result": str(e)
        }
    


@app.get("/vm_info/{moid}")
def get_vm_info(moid: str): # 2. Accept the variable directly from the URL path
    try:
        # 3. Pass the path variable directly into the subprocess command
        cmd = ["python3", "vm_info.py", moid]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        parsed_data = ast.literal_eval(result.stdout.rstrip())
        
        # Fetch metadata from Database
        async def _query():
            conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
            try:
                # 1. Try to find by vcenter_uuid first (used when active)
                row = await conn.fetchrow(
                    "SELECT owner, shutdown_date, deletion_date, created_at as created_date, status as state "
                    "FROM terraform_remote_state.state_metadata "
                    "WHERE vcenter_uuid = $1;",
                    moid
                )
                if row:
                    return dict(row)
                
                # 2. It might fail if created_at doesn't exist
                row = await conn.fetchrow(
                    "SELECT owner, shutdown_date, deletion_date, status as state "
                    "FROM terraform_remote_state.state_metadata "
                    "WHERE vcenter_uuid = $1;",
                    moid
                )
                if row:
                    return dict(row)
                 
                # 3. If missing, try matching against vcenter_inventory_cache
                # This handles the case where the frontend asks for "pending-..." or standard mo_Id
                # and we need to link it back to state_metadata.
                # Actually, in create_vm, the initial insert is:
                # vcenter_uuid = 'pending-UUID'
                # So we can just check if anything matches this moid directly:
                row = await conn.fetchrow(
                    "SELECT owner, shutdown_date, deletion_date, status as state "
                    "FROM terraform_remote_state.state_metadata "
                    "WHERE vcenter_uuid = $1 OR state_key = $1;",
                    moid.replace('pending-', '') if moid.startswith('pending-') else moid
                )
                if row:
                    return dict(row)
                    
                return {}
            except Exception as e:
                print(f"DB Fetch Error: {e}")
                return {}
            finally:
                await conn.close()
                
        db_data = asyncio.run(_query())
        
        import datetime
        for k, v in db_data.items():
            if isinstance(v, (datetime.datetime, datetime.date)):
                parsed_data[k] = v.isoformat()
            else:
                parsed_data[k] = v

        return {"status": "success", "vm_info": parsed_data}
        
    except subprocess.CalledProcessError as e:
        # Catch standard subprocess failures (e.g., script exited with code 1)
        raise HTTPException(
            status_code=500, 
            detail=f"Script failed with exit code {e.returncode}. Stderr: {e.stderr}"
        )
    except Exception as e:
        # Catch generic Python errors (e.g., FileNotFoundError, ast parsing errors)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-folders")
def list_folders():
    try:
        cmd = ["python3", "list-folders.py"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        raw_output = result.stdout.rstrip()
        parsed_folders = ast.literal_eval(raw_output)
        return {"status": "success", "folders": parsed_folders}
    except Exception as e:
        return {f"Error: \n{e}\nOutput: {result.stderr}"}
    

@app.get("/list-templates")
def list_templates():
    try:
        cmd = ["python3", "list-templates.py"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        raw_output = result.stdout.rstrip()
        parsed_templates = ast.literal_eval(raw_output)
        return {"status": "success", "templates": parsed_templates}
    except Exception as e:
        return {"status": "error", "Error message": e}



@app.get("/list-portgroups")
def list_portgroups():
    try:
        cmd = ["python3", "list-portgroups.py"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        raw_output = result.stdout.rstrip()
        parsed_portgroups = ast.literal_eval(raw_output)
        return {"status": "success", "portgroups": parsed_portgroups}
    except Exception as e:
        return {"status": "error", "Error message": e}


@app.get('/vm-ip')
def get_ip():
    try:
        cmd = ["terraform", "-chdir=Terraform",
               "output", "ip"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        raw_output = result.stdout.rstrip()
        parsed_ip = ast.literal_eval(raw_output)
        return {"status": "success", "ip": parsed_ip}
    except Exception as e:
        return {"status": "error", "Error message": e}


# ─── New endpoints for local frontend (replace Appsmith direct DB queries) ───

@app.get("/check_provisioning/{tx_uuid}")
def check_provisioning(tx_uuid: str):
    async def _query():
        conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
        try:
            row = await conn.fetchrow(
                "SELECT status FROM terraform_remote_state.state_metadata WHERE state_key = $1",
                tx_uuid
            )
            return dict(row) if row else None
        finally:
            await conn.close()
    
    try:
        result = asyncio.run(_query())
        if result:
            return {"exists": True, "status": result["status"]}
        return {"exists": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/vm-cache')
def get_vm_cache():
    """Return all cached VMs for sidebar tree."""
    async def _query():
        conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
        try:
            rows = await conn.fetch(
                "SELECT vm_moid, vm_name, folder_name, power_state "
                "FROM terraform_remote_state.vcenter_inventory_cache "
                "ORDER BY folder_name, vm_name;"
            )
            return [dict(r) for r in rows]
        finally:
            await conn.close()
    try:
        vms = asyncio.run(_query())
        return {"status": "success", "vms": vms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/pending-vm/{moid}')
def delete_pending_vm(moid: str):
    """Delete a pending VM record (used for rollback on failure)."""
    async def _delete():
        conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
        try:
            await conn.execute(
                "DELETE FROM terraform_remote_state.vcenter_inventory_cache WHERE vm_moid = $1;",
                moid
            )
        finally:
            await conn.close()
    try:
        asyncio.run(_delete())
        return {"status": "deleted", "moid": moid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TESTS
@app.post("/run-test-script")
def execute_test_script(payload: AppsmithPayload):
    cmd = ["python3", "test-script.py", payload.message]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    return {"status": "success", "script_output": result.stdout.strip()}

@app.get('/list')
def execute_list_script():
    cmd = ["python3", "list-script.py"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True

    )
    parsed_list = result.stdout.rstrip()
    return  {"status": "success", "items": parsed_list}

