FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV CEOSYS_BASE_PATH /
ENV MAGICAPP_SERVER "https://api.magicapp.org"

RUN pip install --upgrade pip
ADD ./apps/guideline-server/requirements.txt .
RUN pip install -r requirements.txt

COPY ./apps/guideline-server /app
COPY ./FHIR /FHIR
