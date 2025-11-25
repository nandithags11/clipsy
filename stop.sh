#!/bin/bash

echo "Stopping Clipsy services..."
docker compose down

echo ""
echo "Services stopped successfully."
echo ""
echo "To remove all data (including database):"
echo "  docker compose down -v"
