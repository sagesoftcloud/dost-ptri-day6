#!/bin/bash
# Start the application in the background
echo "Starting application..."
cd /opt/dost-ptri-app
sudo nohup python3 app.py > /var/log/dost-ptri-app.log 2>&1 &
