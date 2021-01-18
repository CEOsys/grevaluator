FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV CEOSYS_BASE_PATH /

RUN pip install --upgrade pip
ADD ./apps/patientdata-server/requirements.txt .
RUN pip install -r requirements.txt

COPY ./apps/patientdata-server /app
COPY ./data /data
