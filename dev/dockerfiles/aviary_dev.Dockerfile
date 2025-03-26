FROM python:3.12-slim

WORKDIR /aviary

ENV PYTHONUNBUFFERED 1

LABEL org.opencontainers.image.title="aviary" \
    org.opencontainers.image.description="Composable inference and postprocessing pipeline for remote sensing data" \
    org.opencontainers.image.authors="Marius Maryniak (marius.maryniak@w-hs.de)" \
    org.opencontainers.image.licenses="GPL-3.0" \
    org.opencontainers.image.version="dev" \
    org.opencontainers.image.url="https://www.github.com/geospaitial-lab/aviary" \
    org.opencontainers.image.source="https://www.github.com/geospaitial-lab/aviary" \
    org.opencontainers.image.documentation="https://geospaitial-lab.github.io/aviary"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY . .

RUN uv venv venv && \
    . venv/bin/activate && \
    uv pip install --upgrade pip setuptools wheel && \
    uv pip install huggingface_hub onnxruntime && \
    uv pip install . && \
    adduser --disabled-password --gecos "" aviary_user

USER aviary_user

ENV PATH="/aviary/venv/bin:$PATH"

ENTRYPOINT ["aviary"]
