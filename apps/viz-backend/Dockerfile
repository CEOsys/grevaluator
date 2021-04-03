FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV CEOSYS_BASE_PATH /

COPY ./apps/viz-backend /app
COPY ./data /data

RUN pip install --upgrade pip
ADD ./apps/viz-backend/requirements.txt .
RUN pip install -r requirements.txt
