FROM alpine:latest
RUN apk add libpq-dev python-dev alpine-sdk postgresql-dev python3
RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN pip3 install -r requirements.txt
CMD ["python3", "/app/sql_inserts.py"]