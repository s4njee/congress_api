FROM alpine:latest
RUN apk add libpq-dev alpine-sdk postgresql-dev pypy3 py3-pip libxml2-dev libxslt-dev py3-lxml pypy-dev
RUN ln -sf /usr/bin/python3 /usr/bin/python
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
RUN pip3 install -r requirements.txt
ADD . /app/
CMD ["pypy3", "/app/sql_inserts.py"]
