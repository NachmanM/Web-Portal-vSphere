FROM python:3.12-slim

WORKDIR /code



RUN apt-get update && apt-get install -y gnupg curl ca-certificates && \
    curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com bookworm main" > /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && apt-get install -y terraform && \
    rm -rf /var/lib/apt/lists/*

COPY requirments.txt:.

RUN apt update && pip install -r requirements.txt

COPY . .

EXPOSE 5672