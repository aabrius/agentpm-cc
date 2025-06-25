#!/bin/bash

echo "=== AgentPM MVP Test Script ==="
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"

# Start services
echo
echo "Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo
echo "Waiting for services to be ready..."
sleep 10

# Check PostgreSQL
echo
echo "Checking PostgreSQL..."
docker-compose exec -T db psql -U postgres -d agentpm -c "SELECT 1" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
fi

# Check Redis
echo
echo "Checking Redis..."
docker-compose exec -T redis redis-cli ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis is not ready"
fi

# Check Backend API
echo
echo "Checking Backend API..."
curl -s http://localhost:8000/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend API is ready"
    echo "   API Docs: http://localhost:8000/docs"
else
    echo "❌ Backend API is not ready"
fi

# Check Frontend
echo
echo "Checking Frontend..."
curl -s http://localhost:3000 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Frontend is ready"
    echo "   UI: http://localhost:3000"
else
    echo "❌ Frontend is not ready"
fi

echo
echo "=== MVP Status ==="
echo "Backend WebSocket: ws://localhost:8000/ws/{conversation_id}"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo
echo "To view logs: docker-compose logs -f [service_name]"
echo "To stop: docker-compose down"