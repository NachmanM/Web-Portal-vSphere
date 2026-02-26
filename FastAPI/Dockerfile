FROM python:3.12-slim

WORKDIR /FastAPI

RUN apt update && pip3 install uvicorn

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./
COPY test-script.py ./

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
