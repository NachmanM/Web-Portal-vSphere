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
import aio_pika
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
async def create_vm(payload: VMCreation):
    async with await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/") as conn:
        async with conn.channel() as channel:
            queue = await channel.declare_queue("create_vm")
            msg_body = payload.model_dump_json().encode('utf-8')
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=msg_body,
                    content_type='application/json'
                ),
                routing_key=queue.name
                
            )    
    return {"status": "Message accepted", "queue": queue.name}
    


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
        return {"status": "error", "Error message": repr(e)}


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
                "SELECT status, vcenter_uuid FROM terraform_remote_state.state_metadata WHERE state_key = $1",
                tx_uuid
            )
            return dict(row) if row else None
        finally:
            await conn.close()
    
    try:
        result = asyncio.run(_query())
        if result:
            return {
                "exists": True, 
                "status": result["status"],
                "vcenter_uuid": result["vcenter_uuid"]
            }
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

