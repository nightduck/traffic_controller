#!/bin/bash

# Ensure the script is run with root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or using sudo"
  exit 1
fi

# Define the service name and path
SERVICE_NAME="traffic_controller.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"
# IMPORTANT: Adjust this path if your project is not in /home/pi/traffic_controller
PROJECT_DIR=$(pwd)
PYTHON_EXEC="/usr/bin/python3" # Verify with 'which python3' on your Pi

echo "Creating systemd service file at ${SERVICE_PATH}..."

# Create the systemd unit file content using a heredoc
cat > "${SERVICE_PATH}" << EOF
[Unit]
Description=Traffic Controller Flask Application
After=network.target

[Service]
User=pi
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PYTHON_EXEC} app.py
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=traffic-controller

[Install]
WantedBy=multi-user.target
EOF

# Set correct permissions for the service file
chmod 644 "${SERVICE_PATH}"

echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Enabling ${SERVICE_NAME} to start on boot..."
systemctl enable "${SERVICE_NAME}"

echo "Installation complete."
echo "You can start the service now with: sudo systemctl start ${SERVICE_NAME}"
echo "You can check the status with: sudo systemctl status ${SERVICE_NAME}"
echo "You can view logs with: sudo journalctl -u ${SERVICE_NAME} -f"

exit 0

