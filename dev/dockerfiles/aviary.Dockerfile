FROM python:3.12-slim-bookworm AS builder

WORKDIR /aviary

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY . .

RUN uv venv venv && \
    . venv/bin/activate && \
    uv pip install --upgrade pip setuptools wheel && \
    uv pip install .[all] && \
    uv pip install huggingface_hub onnxruntime

FROM python:3.12-slim-bookworm AS runner

WORKDIR /aviary

ENV PYTHONUNBUFFERED=1

ARG CREATED
ARG VERSION

LABEL org.opencontainers.image.authors="Marius Maryniak (marius.maryniak@w-hs.de)" \
    org.opencontainers.image.created=$CREATED \
    org.opencontainers.image.description="Python Framework for tile-based processing of geospatial data" \
    org.opencontainers.image.documentation="https://geospaitial-lab.github.io/aviary" \
    org.opencontainers.image.licenses="GPL-3.0" \
    org.opencontainers.image.source="https://www.github.com/geospaitial-lab/aviary" \
    org.opencontainers.image.title="aviary" \
    org.opencontainers.image.url="https://www.github.com/geospaitial-lab/aviary" \
    org.opencontainers.image.version=$VERSION

COPY --from=builder /aviary/venv /aviary/venv

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libexpat1 \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    adduser --disabled-password --gecos "" aviary_user && \
    chown aviary_user:aviary_user /aviary

USER aviary_user

ENV PATH="/aviary/venv/bin:$PATH"

ENTRYPOINT ["aviary"]
