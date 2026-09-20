FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir uv==0.9.7

WORKDIR /src
COPY . .
RUN uv build --out-dir /dist \
    && uv build --out-dir /dist lattence-api

FROM python:3.12-slim AS runtime

RUN useradd --create-home --uid 1000 lattence
WORKDIR /home/lattence

COPY --from=builder /dist/*.whl /tmp/dist/
RUN pip install --no-cache-dir /tmp/dist/*.whl \
    && rm -rf /tmp/dist

USER lattence

EXPOSE 8000
ENTRYPOINT ["lattence", "serve", "--host", "0.0.0.0", "--port", "8000"]
