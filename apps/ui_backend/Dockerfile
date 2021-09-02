FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV CEOSYS_BASE_PATH /
ENV CEOSYS_DATA_PATH /var/data
ENV GUIDELINE_SERVER http://guideline-interface:80
ENV PATIENTDATA_SERVER http://clinical-data-interface:80

RUN pip install --upgrade pip
ADD requirements.txt .
RUN pip install -r requirements.txt

COPY ./app /app
