FROM python:latest

RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN pip install -r requirements.txt
RUN git submodule init
RUN git submodule update
CMD ["python", "/app/sql_inserts.py"]