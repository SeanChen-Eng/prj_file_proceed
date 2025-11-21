#!/bin/bash

# Install required packages
echo "Installing required packages..."
pip3 install Django>=5.2.8
pip3 install PyMuPDF>=1.23.0
pip3 install Pillow>=10.0.0
pip3 install requests>=2.31.0
pip3 install python-dotenv>=1.0.0

# Create and apply migrations
echo "Creating migrations..."
python3 manage.py makemigrations file_processor

echo "Applying migrations..."
python3 manage.py migrate

# Create superuser (optional)
echo "To create a superuser, run: python3 manage.py createsuperuser"

echo "Setup complete! Run 'python3 manage.py runserver 0.0.0.0:8000' to start the server on all interfaces."

# 查看当前进程（确认 PID）
#ps aux | grep gunicorn | grep prj_file_proceed | grep -v grep

# 优雅停止（推荐）
pkill -f 'prj_file_proceed.wsgi:application'

# 然后重新启动（在项目根、在 venv 已激活或使用相对路径）
#nohup .venv/bin/gunicorn prj_file_proceed.wsgi:application --bind 0.0.0.0:8080 --workers 3 > gunicorn.log 2>&1 &