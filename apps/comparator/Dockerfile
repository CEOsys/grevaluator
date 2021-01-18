FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV CEOSYS_BASE_PATH /
ENV GUIDELINE_SERVER http://guideline-server:80
ENV PATIENTDATA_SERVER http://patientdata-server:80
ENV CEOSYS_DATA_PATH /var/data

RUN pip install --upgrade pip
ADD ./apps/comparator/requirements.txt .
RUN pip install -r requirements.txt

COPY ./apps/comparator /app
COPY ./apps/comparator/res /res
