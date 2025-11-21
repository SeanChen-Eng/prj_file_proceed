#!/usr/bin/env bash
# Simple "playground" deployment helper for prj_file_proceed
# Usage (on the server, in project root):
#   sudo bash deploy/playground_setup.sh
# The script will:
# - create a venv (optional)
# - install requirements
# - run makemigrations/migrate
# - collectstatic
# - install gunicorn
# - write a systemd unit (requires sudo)
# - start & enable the service

set -euo pipefail

PROJECT_DIR="/home/$(whoami)/django/prj_file_proceed"
VENV_DIR="$PROJECT_DIR/.venv"
SERVICE_NAME="gunicorn_prj_file_proceed"
SYSTEMD_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
PYTHON_BIN="$VENV_DIR/bin/python"
GUNICORN_BIN="$VENV_DIR/bin/gunicorn"
ENV_FILE="$PROJECT_DIR/.env"

echo "Project dir: $PROJECT_DIR"

# 1) Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating venv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

# 2) Activate and install requirements
source "$VENV_DIR/bin/activate"
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  pip install gunicorn django PyMuPDF Pillow requests
fi

# 3) Create .env if missing (sensible defaults)
if [ ! -f "$ENV_FILE" ]; then
  cat > "$ENV_FILE" <<EOF
# Example .env - DO NOT COMMIT to git
DEBUG=False
SECRET_KEY=replace-with-secure-secret
ALLOWED_HOSTS=localhost,127.0.0.1
DIFY_API_KEY=
DIFY_USER=
DIFY_SERVER=
EOF
  echo "Created example .env at $ENV_FILE - edit secrets before production use"
fi

# 4) Django migrations and collectstatic
echo "Applying migrations..."
$PYTHON_BIN manage.py makemigrations
$PYTHON_BIN manage.py migrate

echo "Collecting static files..."
$PYTHON_BIN manage.py collectstatic --noinput

# 5) Ensure gunicorn installed
if [ ! -x "$GUNICORN_BIN" ]; then
  pip install gunicorn
fi

# 6) Write systemd unit (requires sudo)
if [ "$EUID" -ne 0 ]; then
  echo "Note: writing systemd unit requires sudo. You will be prompted for sudo now."
fi
sudo tee "$SYSTEMD_PATH" > /dev/null <<EOF
[Unit]
Description=gunicorn daemon for prj_file_proceed (playground)
After=network.target

[Service]
User=$(whoami)
Group=$(id -gn)
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$GUNICORN_BIN prj_file_proceed.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"

echo "Service $SERVICE_NAME started. You can check logs with: sudo journalctl -u $SERVICE_NAME -f"

echo "Playground deployment complete. The app should be reachable via nginx or by port-forwarding to 127.0.0.1:8000"

# End of script

# 查看当前进程（确认 PID）
#ps aux | grep gunicorn | grep prj_file_proceed | grep -v grep

# 优雅停止（推荐）
#pkill -f 'prj_file_proceed.wsgi:application'

# 然后重新启动（在项目根、在 venv 已激活或使用相对路径）
#nohup .venv/bin/gunicorn prj_file_proceed.wsgi:application --bind 0.0.0.0:8080 --workers 3 > gunicorn.log 2>&1 &
