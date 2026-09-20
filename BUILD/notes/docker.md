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
