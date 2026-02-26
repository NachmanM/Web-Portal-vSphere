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
