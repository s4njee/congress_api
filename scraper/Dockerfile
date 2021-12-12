FROM python:latest

RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN pip install -r requirements.txt
CMD ["python", "/app/sql_inserts.py"]