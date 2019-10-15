FROM alpine:edge
RUN apk update \
  && apk add --no-cache python3
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY upload.py upload.py
CMD python3 upload.py