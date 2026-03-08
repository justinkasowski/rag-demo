#!/bin/bash
set -e

echo "Starting Ollama..."
ollama serve &

echo "Waiting for Ollama to start..."
sleep 5

echo "Pulling model ${MODEL}"
ollama pull ${MODEL}

echo "Starting API..."
uvicorn main:app --host 0.0.0.0 --port ${PORT}