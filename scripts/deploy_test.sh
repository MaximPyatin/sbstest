#!/usr/bin/env bash

set -euo pipefail

if [[ -z "${KUBE_CONFIG_B64:-}" ]]; then
  echo "::error::KUBE_CONFIG_B64 secret is not set. Unable to deploy."
  exit 1
fi

IMAGE_REF="${1:-}"
if [[ -z "${IMAGE_REF}" ]]; then
  echo "::error::Container image reference argument is required."
  exit 1
fi

NAMESPACE="${KUBE_NAMESPACE:-default}"
RELEASE_NAME="${HELM_RELEASE:-sbs}"
CHART_DIR="deploy/helm/sbs"

WORK_DIR="$(mktemp -d)"
KUBECONFIG_FILE="${WORK_DIR}/kubeconfig"
trap 'rm -rf "${WORK_DIR}"' EXIT

echo "${KUBE_CONFIG_B64}" | base64 --decode > "${KUBECONFIG_FILE}"
export KUBECONFIG="${KUBECONFIG_FILE}"

# Verify access to the cluster before applying manifests.
if ! kubectl version --request-timeout=5s >/dev/null 2>&1; then
  echo "::warning::Unable to reach the Kubernetes API server. Skipping deployment step."
  exit 0
fi

# Split image reference into repository and tag.
IMAGE_REPOSITORY="${IMAGE_REF%:*}"
IMAGE_TAG="${IMAGE_REF##*:}"
if [[ "${IMAGE_REPOSITORY}" == "${IMAGE_TAG}" ]]; then
  IMAGE_REPOSITORY="${IMAGE_REF}"
  IMAGE_TAG="latest"
fi

helm dependency build "${CHART_DIR}"

HELM_SET_ARGS=(
  "--set" "global.environment=test"
  "--set" "stack.api.image.repository=${IMAGE_REPOSITORY}"
  "--set" "stack.api.image.tag=${IMAGE_TAG}"
  "--set" "stack.api.image.pullPolicy=Always"
  "--set" "stack.worker.image.repository=${IMAGE_REPOSITORY}"
  "--set" "stack.worker.image.tag=${IMAGE_TAG}"
  "--set" "stack.worker.image.pullPolicy=Always"
)

if [[ -n "${IMAGE_PULL_SECRET:-}" ]]; then
  HELM_SET_ARGS+=("--set-string" "global.imagePullSecrets[0].name=${IMAGE_PULL_SECRET}")
fi

helm upgrade --install "${RELEASE_NAME}" "${CHART_DIR}" \
  --namespace "${NAMESPACE}" \
  --create-namespace \
  "${HELM_SET_ARGS[@]}" \
  --wait \
  --timeout 10m
