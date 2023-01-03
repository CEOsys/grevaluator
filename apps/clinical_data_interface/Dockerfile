FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

ENV CEOSYS_BASE_PATH /

RUN pip install --upgrade pip
ADD requirements.txt .
RUN pip install -r requirements.txt

COPY ./app /app
COPY ./data /data
