#!/bin/bash
set -e

echo "Starting Ollama..."
ollama serve &

echo "Waiting for Ollama to start..."
sleep 5


echo "Starting API..."
uvicorn main:app --host 0.0.0.0 --port ${PORT}
