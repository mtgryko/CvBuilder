#!/bin/sh
ollama serve &

# Wait for the server to start
sleep 5

# Ensure the model is available (pull if missing)
if ! ollama list | grep -q "$MODEL"; then
    echo "Model $MODEL not found. Pulling..."
    ollama pull $MODEL
else
    echo "Model $MODEL already present."
fi

# Keep Ollama running in foreground
wait
