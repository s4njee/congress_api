FROM python:alpine
RUN apk add py3-pip
RUN pip3 install -r requirements.txt
RUN mkdir /app
WORKDIR /app
ADD . /app/
CMD ["python", "/app/sql_inserts.py"]