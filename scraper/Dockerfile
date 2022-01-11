FROM alpine:latest
RUN apk add libpq-dev python3-dev alpine-sdk postgresql-dev python3 py3-pip libxml2-dev libxslt-dev py3-lxml
RUN ln -sf /usr/bin/python3 /usr/bin/python
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
RUN pip3 install -r requirements.txt
ADD . /app/
CMD ["python3", "/app/sql_inserts.py"]
