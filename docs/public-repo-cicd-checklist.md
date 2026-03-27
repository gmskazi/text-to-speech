# Public Repo CI/CD Checklist (No Self-Hosted Runner)

Use this checklist to track the new deployment model:

- GitHub-hosted CI only
- Local Docker image builds only (no registry push)
- Local server does local build-and-deploy
- Cloudflare Tunnel for external access

## 1) Cleanup and Safety

- [ ] Remove any self-hosted runner from repository settings
- [ ] Ensure no workflow uses `self-hosted`
- [ ] Confirm no production secrets are stored in GitHub Actions secrets

## 2) GitHub CI (Hosted Runners)

- [x] CI runs on `ubuntu-latest`
- [x] Lint configured (`ruff check .`)
- [x] Type checks configured (`mypy app tests`)
- [x] Tests configured (`pytest -q`)
- [x] Secret scan enabled in CI (`gitleaks`)
- [x] Dependency audit enabled in CI (`pip-audit`)
- [x] Docker build smoke check enabled in CI

## 3) Local Container Build

- [x] Build container in CI as smoke check (no push)
- [ ] Build container on local server for deployment
- [ ] Tag local deploy image consistently (for rollback)
- [ ] Keep previous local image/tag available for rollback

## 4) Local Server Build-and-Deploy

- [ ] Install Docker + Compose on server
- [ ] Add deploy script that:
  - [ ] pulls latest code (or target ref)
  - [ ] builds image locally
  - [ ] runs `docker compose up -d`
  - [ ] verifies `/health`
  - [ ] rolls back on failure
- [ ] Schedule script via systemd timer (or cron)

## 5) Cloudflare Tunnel Runtime

- [ ] Cloudflare tunnel configured for `tts.madeeasyit.com`
- [ ] `cloudflared` container runs in compose
- [ ] App is reachable at `https://tts.madeeasyit.com/health`
- [ ] No inbound app port exposed publicly

## 6) Secrets Management (Bitwarden)

- [ ] Store `CLOUDFLARE_TUNNEL_TOKEN` in Bitwarden Secrets Manager
- [ ] Store `BWS_ACCESS_TOKEN` only on local server
- [ ] Resolve secrets at runtime on server (never commit `.env` with real secrets)

## 7) GitHub Security Controls

- [ ] Enable secret scanning
- [ ] Enable push protection
- [ ] Set branch protection on `main`
- [ ] Require CI checks before merge
- [ ] Disallow force pushes to `main`

## 8) Validation

- [ ] CI passes on pull requests
- [ ] Server build-and-deploy workflow works locally
- [ ] Health endpoint is stable after redeploy
- [ ] Rollback path tested and documented
