# Deploy to Cloud Run (private, Google SSO)

Deploy Aegis as an internal web app on **Google Cloud Run**, protected by
**Identity-Aware Proxy (IAP)** so only accounts in your Google Workspace domain
(e.g. `@google.com`) can sign in. No load balancer required.

The whole thing is one command:

```bash
./deploy.sh
```

---

## What you get

- A containerized single image (frontend built + served by the FastAPI backend).
- **IAP** in front of the `run.app` URL → Google sign-in required.
- Access restricted to **`domain:google.com`** (configurable).
- The Gemini key stored in **Secret Manager** (not baked into the image or env).
- Local-folder scanning **disabled** in the cloud (users scan via GitHub URL or `.zip`).

## Prerequisites

1. **gcloud CLI**, authenticated: `gcloud auth login`
2. A **GCP project that belongs to an organization** (required for direct IAP).
   IAP uses a Google-managed OAuth client, so by default only users *in your org*
   can authenticate.
3. Roles to run the script: Owner, or a combination that can enable APIs, deploy to
   Cloud Run, manage Secret Manager, and set IAP/IAM policy.
4. A **Gemini API key** in `.env` (`GEMINI_API_KEY=…`) or exported in your shell.

## Deploy

```bash
# pick your project (once)
gcloud config set project YOUR_PROJECT

# optional overrides
export AEGIS_REGION=us-central1        # default
export AEGIS_SERVICE=aegis             # default
export AEGIS_ALLOWED_DOMAIN=google.com # default

./deploy.sh
```

The script:

1. Enables the required APIs (Run, IAP, Cloud Build, Artifact Registry, Secret Manager).
2. Stores your key in Secret Manager (`aegis-gemini-key`) and grants the runtime
   service account access.
3. Builds from source and deploys to Cloud Run with `--no-allow-unauthenticated --iap`.
4. Creates the IAP service agent and grants it `roles/run.invoker`.
5. Grants `roles/iap.httpsResourceAccessor` to `domain:google.com`.
6. Prints the URL.

> First-time IAP enablement occasionally needs a minute for the service agent to
> provision — if step 5/6 errors once, re-run `./deploy.sh` (it's idempotent).

## Test it

Open the printed URL. You'll be sent through Google sign-in; a `@google.com` account
gets in, anyone else gets a 403. IAM can take a few minutes to propagate right after
the first enable.

## Grant access to specific people or a group

By default the whole domain is allowed. To scope it tighter, remove the domain grant
and add a group or users instead:

```bash
gcloud beta iap web add-iam-policy-binding \
  --resource-type=cloud-run --service=aegis --region=us-central1 \
  --member="group:my-team@google.com" --role=roles/iap.httpsResourceAccessor
```

## Update / redeploy

Just run `./deploy.sh` again — it adds a new secret version (if the key changed) and
ships a new revision.

## Rotate the key

```bash
printf '%s' "NEW_KEY" | gcloud secrets versions add aegis-gemini-key --data-file=-
gcloud run services update aegis --region us-central1   # picks up :latest
```

## Tear down

```bash
gcloud run services delete aegis --region us-central1
gcloud secrets delete aegis-gemini-key
```

## Notes & troubleshooting

- **403 after sign-in** — your account isn't in an allowed domain/group, or IAM hasn't
  propagated yet (wait a few minutes).
- **Key security** — the key lives only in Secret Manager and is mounted as an env var
  at runtime; it is never in the image (`.env` is in `.dockerignore`).
- **Custom runtime service account** — the script uses the default Compute SA. To use a
  dedicated SA, add `--service-account` to the `gcloud run deploy` line and grant that
  SA `roles/secretmanager.secretAccessor` on the secret.
- **Costs** — Cloud Run scales to zero; you pay per request/compute. Gemini API usage is
  billed separately by your key's project.
