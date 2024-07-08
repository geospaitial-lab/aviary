FROM python:3.12-slim as builder

WORKDIR /aviary

COPY . .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir wheels .

FROM python:3.12-slim as runner

WORKDIR /aviary

COPY --from=builder /aviary/wheels wheels

ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir wheels/* && rm -rf wheels

ENTRYPOINT ["aviary"]
