FROM python:3.12-slim

RUN apt update && pip3 install uvicorn 

#Install Terraform
RUN apt-get update && apt-get install -y gnupg curl ca-certificates && \
    curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com bookworm main" > /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && apt-get install -y terraform && \
    rm -rf /var/lib/apt/lists/*

    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /FastAPI

COPY code/ ./

EXPOSE 8000
EXPOSE 5672

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
