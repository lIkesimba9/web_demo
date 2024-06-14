#!/bin/bash

# Проверка наличия аргумента
if [ -z "$1" ]
then
  echo "Необходимо передать GOOGLE_API_KEY в качестве первого аргумента."
  exit 1
fi

GOOGLE_API_KEY=$1

# Create .env file for environment variables
echo "GOOGLE_API_KEY=${GOOGLE_API_KEY}" > ./web_demo/backend/.env

# Install and run 'ollama'
curl -fsSL https://ollama.com/install.sh | sh
ollama run llama3

# Run Docker Compose
docker-compose up --build

