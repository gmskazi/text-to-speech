#!/usr/bin/env bash
set -euo pipefail

IMAGE_REPO="${IMAGE_REPO:-text-to-speech}"
CURRENT_TAG="${CURRENT_TAG:-deploy-current}"
PREVIOUS_TAG="${PREVIOUS_TAG:-deploy-previous}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/health}"
HEALTH_TIMEOUT_SECONDS="${HEALTH_TIMEOUT_SECONDS:-120}"
AUTO_PULL="${AUTO_PULL:-true}"
GIT_REMOTE="${GIT_REMOTE:-origin}"
DEPLOY_REF="${DEPLOY_REF:-main}"

CURRENT_IMAGE="${IMAGE_REPO}:${CURRENT_TAG}"
PREVIOUS_IMAGE="${IMAGE_REPO}:${PREVIOUS_TAG}"

wait_for_health() {
  local url="$1"
  local timeout="$2"
  python3 - "$url" "$timeout" <<'PY'
import sys
import time
import urllib.request

url = sys.argv[1]
timeout = int(sys.argv[2])
deadline = time.time() + timeout

while time.time() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if 200 <= response.status < 300:
                sys.exit(0)
    except Exception:
        pass
    time.sleep(2)

sys.exit(1)
PY
}

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "Compose file not found: ${COMPOSE_FILE}" >&2
  exit 1
fi

if [[ "${AUTO_PULL}" == "true" ]]; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Updating repository to ${GIT_REMOTE}/${DEPLOY_REF}..."
    git fetch --prune "${GIT_REMOTE}"
    git checkout -q "${DEPLOY_REF}"
    git reset --hard "${GIT_REMOTE}/${DEPLOY_REF}"
  else
    echo "AUTO_PULL is true but current directory is not a git repository." >&2
    exit 1
  fi
fi

echo "Building local deploy image..."
bash scripts/build_local_image.sh

export IMAGE_REPO
export APP_IMAGE_TAG="${CURRENT_TAG}"

echo "Starting app with Docker Compose..."
docker compose -f "${COMPOSE_FILE}" up -d --remove-orphans

echo "Checking health: ${HEALTH_URL}"
if wait_for_health "${HEALTH_URL}" "${HEALTH_TIMEOUT_SECONDS}"; then
  echo "Deploy succeeded."
  exit 0
fi

echo "Deploy health check failed. Attempting rollback..." >&2

if docker image inspect "${PREVIOUS_IMAGE}" >/dev/null 2>&1; then
  docker tag "${PREVIOUS_IMAGE}" "${CURRENT_IMAGE}"
  docker compose -f "${COMPOSE_FILE}" up -d --remove-orphans

  if wait_for_health "${HEALTH_URL}" "${HEALTH_TIMEOUT_SECONDS}"; then
    echo "Rollback succeeded." >&2
    exit 1
  fi

  echo "Rollback failed health check as well." >&2
  exit 1
fi

echo "No previous image tag available for rollback: ${PREVIOUS_IMAGE}" >&2
exit 1
