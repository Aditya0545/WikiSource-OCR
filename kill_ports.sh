#!/bin/bash

# Kill all processes using port 5000 (backend)
echo "Killing all processes using port 5000..."
fuser -k 5000/tcp 2>/dev/null

# Kill all processes using port 3000 (frontend)
echo "Killing all processes using port 3000..."
fuser -k 3000/tcp 2>/dev/null

echo "All processes on ports 5000 and 3000 have been killed." 