FROM python:3.12-slim

WORKDIR /aviary

COPY . .

ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir .

ENTRYPOINT ["aviary"]
