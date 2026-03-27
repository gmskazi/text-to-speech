# Ansible Server Setup

This playbook configures a server for local build-and-deploy using Docker Compose.

## What it configures

- Installs Docker Engine and Docker Compose plugin
- Clones this repository to the server
- Installs `tts-deploy.service` + `tts-deploy.timer`
- Uses `scripts/deploy_local.sh` for local image build, health verification, and rollback

## 1) Prepare inventory

Copy the example inventory and set your host:

```bash
cd infra/ansible
cp inventory.ini.example inventory.ini
```

Example host entry:

```ini
[tts_servers]
tts-prod ansible_host=203.0.113.10 ansible_user=ubuntu
```

## 2) Review variables

Defaults are in `group_vars/all.yml`.

Common values to change:

- `tts_repo_url`
- `tts_repo_ref`
- `tts_app_root`
- `tts_deploy_on_calendar`
- `tts_app_port_bind`

## 3) Run the playbook

```bash
cd infra/ansible
ansible-playbook playbook.yml
```

## 4) Optional initial deploy

Set this variable to run deploy immediately during playbook run:

```yaml
tts_run_initial_deploy: true
```

## Service controls on server

```bash
sudo systemctl status tts-deploy.timer
sudo systemctl start tts-deploy.service
sudo journalctl -u tts-deploy.service -n 200 --no-pager
```
