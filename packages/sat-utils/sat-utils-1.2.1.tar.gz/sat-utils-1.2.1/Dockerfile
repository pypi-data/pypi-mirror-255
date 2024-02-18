FROM satregistry.ehps.ncsu.edu/it/python-image:latest

WORKDIR /utils

RUN apt update
RUN apt install -y unixodbc
RUN apt install -y unixodbc-dev

COPY requirements.txt .
RUN python3 -m pip install -r requirements/base/base.txt --extra-index-url https://pypi.ehps.ncsu.edu

ENV PATH="/app/oracle/instantclient_21_4:/app/oracle/instantclient_21_4/lib:${PATH}"

ENV LD_LIBRARY_PATH="/app/oracle/instantclient_21_4"

ENV port 8080

EXPOSE $port

COPY . .
