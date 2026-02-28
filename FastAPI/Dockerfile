FROM python:3.12-slim

WORKDIR /FastAPI

RUN apt update && pip3 install uvicorn 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Install Terraform
# Install dependencies, add HashiCorp repo, and install Terraform in one layer
RUN apt-get update && apt-get install -y gnupg curl ca-certificates && \
    curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com bookworm main" > /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && apt-get install -y terraform && \
    rm -rf /var/lib/apt/lists/*


COPY code/ ./

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
