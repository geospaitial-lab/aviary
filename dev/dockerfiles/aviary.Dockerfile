FROM python:3.12-slim as builder

WORKDIR /aviary

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY . .

RUN uv venv venv && \
    . venv/bin/activate && \
    uv pip install --upgrade pip setuptools wheel && \
    uv build --wheel --no-cache .

FROM python:3.12-slim as runner

WORKDIR /aviary

ENV PYTHONUNBUFFERED 1

ARG VERSION

LABEL org.opencontainers.image.title="aviary" \
    org.opencontainers.image.description="Composable inference and postprocessing pipeline for remote sensing data" \
    org.opencontainers.image.authors="Marius Maryniak (marius.maryniak@w-hs.de)" \
    org.opencontainers.image.licenses="GPL-3.0" \
    org.opencontainers.image.version=$VERSION \
    org.opencontainers.image.url="https://www.github.com/geospaitial-lab/aviary" \
    org.opencontainers.image.source="https://www.github.com/geospaitial-lab/aviary" \
    org.opencontainers.image.documentation="https://geospaitial-lab.github.io/aviary"

COPY --from=builder /bin/uv /bin/uv
COPY --from=builder /aviary/venv /aviary/venv
COPY --from=builder /aviary/dist /aviary/dist

RUN uv venv venv && \
    . venv/bin/activate && \
    uv pip install --no-cache dist/* && \
    rm -rf dist && \
    adduser --disabled-password --gecos "" aviary_user

USER aviary_user

ENV PATH="/aviary/venv/bin:$PATH"

ENTRYPOINT ["aviary"]
