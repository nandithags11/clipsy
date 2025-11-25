#!/bin/bash

echo "================================================"
echo "  Starting Clipsy Video Streaming Platform"
echo "================================================"

if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo ".env file created. Please update it with your configuration."
fi

echo ""
echo "Building and starting all services..."
echo ""

docker compose up --build -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

echo ""
echo "================================================"
echo "  Clipsy is now running!"
echo "================================================"
echo ""
echo "Access the application at:"
echo "  - Frontend:     http://localhost"
echo "  - Backend API:  http://localhost:8000/api"
echo "  - Admin Panel:  http://localhost:8000/admin"
echo ""
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "To view logs:"
echo "  docker compose logs -f"
echo ""
echo "To stop services:"
echo "  docker compose down"
echo ""
echo "================================================"
