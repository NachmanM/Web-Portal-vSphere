from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import ast
from dotenv import load_dotenv




VCENTER_PWD = os.getenv("VCENTER_PWD")
app = FastAPI()

class AppsmithPayload(BaseModel):
    message: str

class VMCreation(BaseModel):
    vm_name: str
    folder: str




@app.post('/vm')
def create_vm(payload: VMCreation):
    try:
        cmd = ["terraform", "-chdir=Terraform", "init"]
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True)

        cmd2 = ["terraform", "-chdir=Terraform", "apply",
                 f"-var=vm_name={payload.vm_name}",
                 f"-var=folder={payload.folder}",
                 f"-var=VCENTER_PWD={VCENTER_PWD}", "-auto-approve"]
        result = subprocess.run(
            cmd2,
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "success", "created": f"{payload.message}"}
    except Exception as e:
        print("ERROR:\n")
        return {"status": "failed", "message": str(e)}


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
        return {f"Error: \n{e}"}
    










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