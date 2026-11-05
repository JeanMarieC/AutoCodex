# syntax=docker/dockerfile:1

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — "builder": install the Python dependencies with uv.
# This is a throwaway stage. We only use it to produce the virtual-env; the
# final image won't carry uv, build caches, or anything we don't need to RUN.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Grab the `uv` binary (the package manager this project already uses) straight
# from its official image — no manual install needed.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# uv behaviour for containers:
#  - compile .pyc files so the app starts faster
#  - copy files instead of symlinking (symlinks break when we move the venv)
#  - don't auto-download a Python; the base image already has 3.11
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy ONLY the dependency manifests first. Docker caches each instruction as a
# "layer"; as long as these two files are unchanged, Docker reuses the cached
# install on later builds — so editing your code doesn't reinstall every package.
COPY pyproject.toml uv.lock ./

# Install deps into /app/.venv exactly as pinned in uv.lock (--frozen),
# skipping dev-only tools (--no-dev) and our own app for now
# (--no-install-project) so this cached layer is purely about dependencies.
RUN uv sync --frozen --no-dev --no-install-project

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — "runtime": the lean image we actually ship. Start clean and copy in
# just the finished virtual-env and the application source.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Put the venv on PATH so `uvicorn` resolves; unbuffered logs so output shows up
# immediately in `docker logs`.
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Bring the installed dependencies over from the builder stage.
COPY --from=builder /app/.venv /app/.venv

# Copy the application code.
COPY app ./app

# Document the port the API listens on.
EXPOSE 8000

# Start the server. Bind 0.0.0.0 (not 127.0.0.1) so it's reachable from outside
# the container. No --reload — that's a dev convenience, not for a built image.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
