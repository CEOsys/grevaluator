FROM rocker/shiny-verse:latest

ENV COMPARATOR_SERVER http://adherence-evaluator:80
ENV UI_BACKEND_SERVER http://ui-backend:80

RUN apt-get update && apt-get install -y \
    sudo \
    pandoc \
    pandoc-citeproc \
    libcurl4-gnutls-dev \
    libcairo2-dev \
    libxt-dev \
    libssl-dev \
    libssh2-1-dev

## update system libraries
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean

# install renv & restore packages
RUN R -e 'install.packages("renv")'
RUN R -e 'install.packages("dplyr")'
RUN R -e 'install.packages("ggplot2")'
RUN R -e 'install.packages("stringr")'
RUN R -e 'install.packages("httr")'
RUN R -e 'install.packages("purrr")'
RUN R -e 'install.packages("shinythemes")'
RUN R -e 'install.packages("DT")'
RUN R -e 'install.packages("eeptools")'
RUN R -e 'install.packages("jsonlite")'
RUN R -e 'install.packages("DT")'
RUN R -e 'install.packages("plotly")'
RUN R -e 'install.packages("glue")'
RUN R -e 'install.packages("dotenv")'
RUN R -e 'renv::consent(provided = TRUE)'
RUN R -e 'renv::restore()'

# copy necessary files
## app folder
COPY ./app /app
COPY ./www /app/www

# expose port
EXPOSE 3838

# run app on container start
CMD ["R", "-e", "shiny::runApp('/app', host = '0.0.0.0', port = 3838)"]
