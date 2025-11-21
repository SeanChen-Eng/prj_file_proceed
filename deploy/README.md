Playground deployment helper

This folder contains a simple script to deploy the app in "playground" mode —
not production hardened but suitable for letting others access the app after you
log out of the server.

Steps (on the server):

1. Review and edit `.env` in project root to set SECRET_KEY and ALLOWED_HOSTS.
2. Run the helper script (from project root):

   sudo bash deploy/playground_setup.sh

What it does:
- Creates a Python virtualenv at `.venv` if missing
- Installs requirements (or minimal packages)
- Runs migrations and collectstatic
- Installs and configures gunicorn as a systemd service
- Starts and enables the service so it survives logout/reboot

Notes:
- This is a convenience script intended for temporary testing/playground usage.
- For real production use, follow the full deployment checklist: use HTTPS, a
  proper database, secrets management, monitoring and firewall rules.
