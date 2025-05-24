#!/bin/bash

# Kill any process using port 5000 (backend)
echo "Killing any process using port 5000..."
fuser -k 5000/tcp 2>/dev/null

# Kill any process using port 3000 (frontend)
echo "Killing any process using port 3000..."
fuser -k 3000/tcp 2>/dev/null

# Start backend
echo "Starting backend..."
cd backend
nohup python app.py > ../backend.log 2>&1 &
cd ..

# Start frontend
echo "Starting frontend..."
cd frontend
nohup npm start > ../frontend.log 2>&1 &
cd ..

echo "Backend running at http://localhost:5000"
echo "Frontend running at http://localhost:3000" 