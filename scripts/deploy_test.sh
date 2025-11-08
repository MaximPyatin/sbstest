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

WORK_DIR="$(mktemp -d)"
KUBECONFIG_FILE="${WORK_DIR}/kubeconfig"
trap 'rm -rf "${WORK_DIR}"' EXIT

echo "${KUBE_CONFIG_B64}" | base64 --decode > "${KUBECONFIG_FILE}"
export KUBECONFIG="${KUBECONFIG_FILE}"

cp deploy/test/* "${WORK_DIR}/"

sed -i "s|IMAGE_PLACEHOLDER|${IMAGE_REF}|g" "${WORK_DIR}/deployment.yaml"

# Verify access to the cluster before applying manifests.
if ! kubectl version --request-timeout=5s >/dev/null 2>&1; then
  echo "::warning::Unable to reach the Kubernetes API server. Skipping deployment step."
  exit 0
fi

kubectl apply --server-side --validate=false -f "${WORK_DIR}/"

kubectl set image \
  deployment/sbs-api \
  sbs-api="${IMAGE_REF}" \
  --namespace "${NAMESPACE}"

kubectl rollout status deployment/sbs-api --namespace "${NAMESPACE}" --timeout=120s

