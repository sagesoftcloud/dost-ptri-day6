#!/bin/bash
# Validate the application is running and healthy
echo "Validating service..."
sleep 3
curl -f http://localhost:8080/health || exit 1
echo "Service is healthy!"
