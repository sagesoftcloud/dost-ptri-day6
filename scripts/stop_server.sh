#!/bin/bash
# Stop the running application (if any)
echo "Stopping application..."
sudo pkill -f "python3 app.py" || true
