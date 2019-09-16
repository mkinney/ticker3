FROM jfloff/alpine-python:3.7-onbuild
COPY static static
COPY templates templates
COPY fetch.py fetch.py
EXPOSE 80
ENTRYPOINT uvicorn fetch:app --host 0.0.0.0 --port 80