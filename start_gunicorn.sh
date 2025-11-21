#!/bin/bash

# File Processor Platform - Gunicorn Startup Script

# Change to project directory
cd "$(dirname "$0")"

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found!"
fi

# Ensure media directory exists and has correct permissions
mkdir -p media/pdfs media/images
chmod 755 media media/pdfs media/images

# Collect static files (for production)
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python3 manage.py migrate

# Start gunicorn
echo "Starting Gunicorn server..."
exec gunicorn -c gunicorn.conf.py prj_file_proceed.wsgi:application

# 查看当前进程（确认 PID）
#ps aux | grep gunicorn | grep prj_file_proceed | grep -v grep

# 优雅停止（推荐）
#pkill -f 'prj_file_proceed.wsgi:application'

# 然后重新启动（在项目根、在 venv 已激活或使用相对路径）
#nohup .venv/bin/gunicorn prj_file_proceed.wsgi:application --bind 0.0.0.0:8080 --workers 3 > gunicorn.log 2>&1 &