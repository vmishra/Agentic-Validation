#!/usr/bin/env bash
#
# Deploy Aegis to Google Cloud Run, protected by Identity-Aware Proxy (IAP) and
# restricted to a single Google Workspace domain (set AEGIS_ALLOWED_DOMAIN).
#
# One command:  ./deploy.sh
#
# Configure via env (all optional except a project + a key):
#   AEGIS_PROJECT           GCP project id      (default: gcloud config's project)
#   AEGIS_REGION            Cloud Run region    (default: us-central1)
#   AEGIS_SERVICE           service name        (default: aegis)
#   AEGIS_ALLOWED_DOMAIN    Workspace domain    (REQUIRED, e.g. your-company.com)
#   AEGIS_MODEL             Gemini model        (default: gemini-3.5-flash)
#   GEMINI_API_KEY          your key            (default: read from ./.env)
#
# Prereqs: gcloud CLI (authenticated), the project must belong to an organization,
# and you need rights to enable APIs + set IAM. See docs/DEPLOY.md.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$ROOT"

PROJECT="${AEGIS_PROJECT:-$(gcloud config get-value project 2>/dev/null || true)}"
REGION="${AEGIS_REGION:-us-central1}"
SERVICE="${AEGIS_SERVICE:-aegis}"
DOMAIN="${AEGIS_ALLOWED_DOMAIN:-}"
MODEL="${AEGIS_MODEL:-gemini-3.5-flash}"
SECRET="aegis-gemini-key"

[ -n "$PROJECT" ] || { echo "✗ No project. Run: gcloud config set project YOUR_PROJECT  (or set AEGIS_PROJECT)"; exit 1; }
[ -n "$DOMAIN" ] || { echo "✗ Set AEGIS_ALLOWED_DOMAIN to your Google Workspace domain, e.g.:"; echo "     AEGIS_ALLOWED_DOMAIN=your-company.com ./deploy.sh"; exit 1; }

# Resolve the API key: env var wins, else read from .env.
KEY="${GEMINI_API_KEY:-}"
if [ -z "$KEY" ] && [ -f .env ]; then KEY="$(grep -E '^GEMINI_API_KEY=' .env | head -1 | cut -d= -f2- || true)"; fi
[ -n "$KEY" ] || { echo "✗ No GEMINI_API_KEY. Put it in .env or export GEMINI_API_KEY=..."; exit 1; }

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')"
IAP_SA="service-${PROJECT_NUMBER}@gcp-sa-iap.iam.gserviceaccount.com"
RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "→ project=$PROJECT  region=$REGION  service=$SERVICE  domain=$DOMAIN"

echo "→ [1/6] enabling APIs…"
gcloud services enable run.googleapis.com iap.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com --project "$PROJECT" -q

echo "→ [2/6] storing the Gemini key in Secret Manager…"
if gcloud secrets describe "$SECRET" --project "$PROJECT" >/dev/null 2>&1; then
  printf '%s' "$KEY" | gcloud secrets versions add "$SECRET" --data-file=- --project "$PROJECT" -q
else
  printf '%s' "$KEY" | gcloud secrets create "$SECRET" --data-file=- --project "$PROJECT" -q
fi
gcloud secrets add-iam-policy-binding "$SECRET" --project "$PROJECT" \
  --member="serviceAccount:${RUNTIME_SA}" --role=roles/secretmanager.secretAccessor -q >/dev/null

echo "→ [3/6] deploying to Cloud Run (build from source) with IAP…"
gcloud beta run deploy "$SERVICE" \
  --source . --project "$PROJECT" --region "$REGION" \
  --no-allow-unauthenticated --iap \
  --memory 1Gi --cpu 1 --timeout 600 --concurrency 8 --max-instances 3 \
  --set-secrets "GEMINI_API_KEY=${SECRET}:latest" \
  --set-env-vars "AEGIS_MODEL=${MODEL},AEGIS_ALLOW_FOLDER=false,GOOGLE_GENAI_USE_VERTEXAI=false" \
  -q

echo "→ [4/6] ensuring the IAP service agent exists…"
gcloud beta services identity create --service=iap.googleapis.com --project "$PROJECT" -q || true

echo "→ [5/6] granting the IAP agent permission to invoke the service…"
gcloud run services add-iam-policy-binding "$SERVICE" --project "$PROJECT" --region "$REGION" \
  --member="serviceAccount:${IAP_SA}" --role=roles/run.invoker -q >/dev/null

echo "→ [6/6] granting access to everyone @${DOMAIN}…"
gcloud beta iap web add-iam-policy-binding \
  --resource-type=cloud-run --service="$SERVICE" --region="$REGION" --project "$PROJECT" \
  --member="domain:${DOMAIN}" --role=roles/iap.httpsResourceAccessor -q >/dev/null

URL="$(gcloud run services describe "$SERVICE" --project "$PROJECT" --region "$REGION" --format='value(status.url)')"
echo ""
echo "✓ Deployed:  $URL"
echo "  Sign-in is required (Google IAP); only @${DOMAIN} accounts are allowed."
echo "  IAM can take a few minutes to propagate on first enable."
