# Docker module notes

`Dockerfile` at the repository root is a two-stage build. The builder stage
installs `uv` and runs `uv build` twice: once for the root `lattence`
package, once for `lattence-api`, producing both wheels in `/dist`. The
runtime stage is a plain `python:3.12-slim` image with both wheels
`pip install`ed, running as a non-root `lattence` user, with
`ENTRYPOINT ["lattence", "serve", "--host", "0.0.0.0", "--port", "8000"]`.

The image intentionally does not use `uv sync` or copy `.venv` from the
builder: it installs the built wheels the same way a real `pip install
lattence lattence-api` user would, so the container tests what ships, not a
development environment. `.dockerignore` excludes `.git`, `.venv`, and the
various tool caches from the build context.

`tests/docker/test_dockerfile.py` shells out to `docker build` and skips
when Docker is not available on the host running the tests (`shutil.which
("docker") is None`), so the suite does not fail in an environment without a
Docker daemon.

`docker-compose.yml` is the team deployment mode: one `lattence-api`
service built from the root `Dockerfile`, `LATTENCE_API_TOKEN` required
through compose's `${VAR:?message}` syntax (compose itself refuses to start
without it, not just the app), and a project directory bind-mounted
read-only at `/data`, defaulting to `examples/vulnerable-agent` via
`LATTENCE_PROJECT_DIR`. `.env.example` documents both variables.
`tests/docker/test_compose.py` runs `docker compose config` and parses the
resolved YAML to assert the token wiring, port, and read-only mount, plus a
second test asserting compose itself rejects starting with no token set.

`tests/docker/test_compose_scan_acceptance.py` is the real end-to-end check:
it runs `docker compose up -d --build`, waits for `/health`, issues a real
HTTP `GET /v1/scan?path=/data` against the mounted `examples/vulnerable-agent`
volume, tears the stack down in a `finally`, and asserts the container's
findings and summary match calling `create_report` directly against the same
project. Manually confirmed once outside the automated test: 13 findings and
an identical summary between the container and the bare CLI, and zero
`socket.connect()` calls traced inside the running container during a scan,
confirming the offline, no-external-network-dependency claim beyond the
declared package dependencies. An earlier attempt used a compose `internal:
true` network to prove this at the container level, but that also blocks the
published port from being reachable from the host on this engine, defeating
the point of a team-reachable API; the socket trace inside the container is
the actual proof instead, and the network stays a plain default bridge.
