#!/bin/bash

# Проверка наличия аргумента
if [ -z "$1" ]
then
  echo "Необходимо передать GOOGLE_API_KEY в качестве первого аргумента."
  exit 1
fi

if [ -z "$2" ]
then
  echo "Необходимо передать TELEGRAM_TOKEN в качестве второго аргумента."
  exit 1
fi

GOOGLE_API_KEY=$1
TELEGRAM_BOT_TOKEN=$2

# Create .env files for environment variables
echo "GOOGLE_API_KEY=${GOOGLE_API_KEY}" > ./gemini-proxy/.env
echo "TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}" > ./telegram-bot/.env

# Install and run 'ollama'
# curl -fsSL https://ollama.com/install.sh | sh
nohup ollama run llama3 &

# Run Docker Compose
docker-compose up --build


