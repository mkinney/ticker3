FROM python:3.8-buster
WORKDIR /usr/src/app
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY ./src /usr/src/app
EXPOSE 80
ENTRYPOINT uvicorn fetch:app --host 0.0.0.0 --port 80