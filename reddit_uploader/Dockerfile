FROM python:3.8-slim-buster
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY upload.py upload.py
CMD python3 upload.py