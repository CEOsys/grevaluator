FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./viz-backend /app
COPY ./data /data

RUN pip install --upgrade pip
ADD ./viz-backend/requirements.txt .
RUN pip install -r requirements.txt
