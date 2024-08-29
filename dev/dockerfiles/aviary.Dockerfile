FROM python:3.12-slim as builder

WORKDIR /aviary

COPY . .

RUN python -m pip install --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --no-deps --wheel-dir wheels .

FROM python:3.12-slim as runner

WORKDIR /aviary

COPY --from=builder /aviary/wheels wheels

ENV PYTHONUNBUFFERED 1

ARG VERSION

LABEL org.opencontainers.image.title="aviary" \
    org.opencontainers.image.description="Composable inference and postprocessing pipeline for remote sensing data" \
    org.opencontainers.image.authors="Marius Maryniak (marius.maryniak@w-hs.de)" \
    org.opencontainers.image.licenses="GPL-3.0" \
    org.opencontainers.image.version=$VERSION \
    org.opencontainers.image.url="https://github.com/geospaitial-lab/aviary" \
    org.opencontainers.image.source="https://github.com/geospaitial-lab/aviary" \
    org.opencontainers.image.documentation="https://geospaitial-lab.github.io/aviary"

RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir wheels/* && \
    rm -rf wheels && \
    adduser --disabled-password --gecos "" aviary_user

USER aviary_user

ENTRYPOINT ["aviary"]
