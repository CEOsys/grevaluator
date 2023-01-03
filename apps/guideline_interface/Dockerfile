FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

ENV CEOSYS_BASE_PATH /
ENV MAGICAPP_SERVER "https://api.magicapp.org"

RUN pip install --upgrade pip
ADD requirements.txt .
RUN pip install -r requirements.txt

COPY ./app /app
COPY ./FHIR /FHIR
