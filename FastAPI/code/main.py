from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess

app = FastAPI()

class AppsmithPayload(BaseModel):
    message: str

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