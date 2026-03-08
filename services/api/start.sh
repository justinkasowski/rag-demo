#!/bin/bash
set -e

ollama serve &
OLLAMA_PID=$!

until curl -s http://127.0.0.1:11434/api/tags > /dev/null; do
  sleep 1
done

ollama pull llama3.2:3b

uvicorn main:app --host 0.0.0.0 --port 8080