FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./patientdata-server /app
COPY ./data /data

RUN pip install --upgrade pip
ADD ./patientdata-server/requirements.txt .
RUN pip install -r requirements.txt
