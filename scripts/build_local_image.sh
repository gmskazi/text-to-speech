#!/usr/bin/env bash
set -euo pipefail

IMAGE_REPO="${IMAGE_REPO:-text-to-speech}"
CURRENT_TAG="${CURRENT_TAG:-deploy-current}"
PREVIOUS_TAG="${PREVIOUS_TAG:-deploy-previous}"
DEPLOY_TAG_PREFIX="${DEPLOY_TAG_PREFIX:-deploy}"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  SHORT_SHA="$(git rev-parse --short HEAD)"
else
  SHORT_SHA="local"
fi

STAMP="$(date -u +%Y%m%d%H%M%S)"
VERSION_TAG="${DEPLOY_TAG_PREFIX}-${STAMP}-${SHORT_SHA}"

CURRENT_IMAGE="${IMAGE_REPO}:${CURRENT_TAG}"
PREVIOUS_IMAGE="${IMAGE_REPO}:${PREVIOUS_TAG}"
VERSION_IMAGE="${IMAGE_REPO}:${VERSION_TAG}"

echo "Preparing local deploy image tags..."
echo "- repo: ${IMAGE_REPO}"
echo "- version tag: ${VERSION_TAG}"

if docker image inspect "${CURRENT_IMAGE}" >/dev/null 2>&1; then
  echo "Tagging existing current image as previous: ${PREVIOUS_IMAGE}"
  docker tag "${CURRENT_IMAGE}" "${PREVIOUS_IMAGE}"
else
  echo "No existing current image found; previous tag unchanged."
fi

echo "Building new local deploy image..."
docker build -t "${VERSION_IMAGE}" -t "${CURRENT_IMAGE}" .

echo "Build complete."
echo "- current:  ${CURRENT_IMAGE}"
echo "- version:  ${VERSION_IMAGE}"

if docker image inspect "${PREVIOUS_IMAGE}" >/dev/null 2>&1; then
  echo "- previous: ${PREVIOUS_IMAGE}"
fi
