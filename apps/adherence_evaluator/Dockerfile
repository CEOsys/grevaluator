FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV CEOSYS_BASE_PATH /
ENV GUIDELINE_SERVER http://guideline-interface:80
ENV PATIENTDATA_SERVER http://clinical-data-interface:80
ENV CEOSYS_DATA_PATH /var/data

RUN pip install --upgrade pip
ADD requirements.txt .
RUN pip install -r requirements.txt

COPY ./app /app
COPY ./res /res
COPY cgr_adherence /app/cgr_adherence
