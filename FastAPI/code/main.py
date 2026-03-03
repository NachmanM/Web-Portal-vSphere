from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import ast
import json
from dotenv import load_dotenv




VCENTER_PWD = os.getenv("VCENTER_PWD")
app = FastAPI()

class AppsmithPayload(BaseModel):
    message: str

class VMCreation(BaseModel):
    vm_name: str
    folder: str
    template: str
    portgroup: str

    is_windows_image: str

    ram_size: int
    cpu_number: int
    disk_size_gb: list


@app.post('/vm')
def create_vm(payload: VMCreation):
    try:
        import uuid
        random_uuid = str(uuid.uuid4())
        
        cmd = ["terraform", "-chdir=Terraform", "init"]
        init_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True)
        
        cmd = ["terraform", "-chdir=Terraform/", "workspace", "new", f"{random_uuid}"]
        workspace_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

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
        apply_result = subprocess.run(
            cmd2,
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "success", "created": f"{apply_result.stdout}"}
    except Exception as e:
        print("ERROR:\n")
        output_result = "None of the commands ran"
        if apply_result:
            output_result = apply_result.stdout
        elif init_result:
            output_result = workspace_result.stdout
        elif workspace_result:
            output_result = workspace_result.stdout
        return {"status": "failed", "message": str(e), "command_result": str(output_result)}


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
        return {f"Error: \n{e}\nOutput: {result}"}
    

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

