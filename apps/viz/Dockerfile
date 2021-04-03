FROM rocker/shiny-verse:latest

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

# copy necessary files
## app folder
COPY ./apps/viz/ ./app

# install renv & restore packages
RUN R -e 'install.packages("renv")'
RUN R -e 'install.packages("shinythemes")'
RUN R -e 'install.packages("DT")'
RUN R -e 'install.packages("eeptools")'
RUN R -e 'install.packages("RCurl")'
RUN R -e 'install.packages("jsonlite")'
RUN R -e 'renv::consent(provided = TRUE)'
RUN R -e 'renv::restore()'

# expose port
EXPOSE 3838

# run app on container start
CMD ["R", "-e", "shiny::runApp('/app', host = '0.0.0.0', port = 3838)"]
