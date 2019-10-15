FROM alpine:edge
RUN apk update \
  && apk add --no-cache --virtual .build-deps gcc python3-dev make musl-dev
RUN echo "http://dl-8.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories \
  && apk update \
  && apk add --no-cache py3-numpy py3-pandas
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
RUN apk del .build-deps
COPY static static
COPY templates templates
COPY fetch.py fetch.py
EXPOSE 80
ENTRYPOINT uvicorn fetch:app --host 0.0.0.0 --port 80