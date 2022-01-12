FROM alpine:latest
RUN apk add libpq-dev python3-dev alpine-sdk postgresql-dev python3 py3-pip libxml2-dev libxslt-dev py3-lxml
RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN pip3 install -r requirements.txt
CMD ["python3", "/app/sql_inserts.py"]