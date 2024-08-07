FROM python:3.12-slim

WORKDIR /aviary

COPY . .

ENV PYTHONUNBUFFERED 1

LABEL org.opencontainers.image.title="aviary" \
    org.opencontainers.image.description="Composable inference and postprocessing pipeline for remote sensing data" \
    org.opencontainers.image.authors="Marius Maryniak (marius.maryniak@w-hs.de)" \
    org.opencontainers.image.licenses="GPL-3.0" \
    org.opencontainers.image.version="dev" \
    org.opencontainers.image.url="https://github.com/geospaitial-lab/aviary" \
    org.opencontainers.image.documentation="https://geospaitial-lab.github.io/aviary"

RUN pip install --no-cache-dir .

ENTRYPOINT ["aviary"]
