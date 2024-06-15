#!/bin/bash

# Проверка наличия аргумента
if [ -z "$1" ]
then
  echo "Необходимо передать TELEGRAM_TOKEN в качестве первого аргумента."
  exit 1
fi

if [ -z "$2" ]
then
  echo "Warning: GOOGLE_API_KEY в качестве второго аргумента не задан. Используется значение по умолчанию 'DUMMY_KEY'."
  GOOGLE_API_KEY="DUMMY_KEY"
else
  GOOGLE_API_KEY=$2
fi

TELEGRAM_BOT_TOKEN=$1

mkdir -p ./frontend/certs && cd ./frontend/certs
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/C=US/ST=California/L=San Francisco/O=MyCompany/OU=MyDepartmenta/CN=mydomaina.com"
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

cd ../..

mkdir -p ./backend/certs && cd ./backend/certs
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/C=US/ST=California/L=San Francisco/O=MyCompany/OU=MyDepartmentb/CN=mydomainb.com"
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

cd ../..

# Проверка наличия третьего аргумента и его значения
if [ "$3" == "RUN_OLLAMA" ]; then
  echo "Запуск установки и запуска ollama"
  curl -fsSL https://ollama.com/install.sh | sh
  ollama run llama3 &
else
  echo "3-й аргумент не задан или не равен RUN_OLLAMA. Пропуск установки и запуска ollama."
fi

# Create .env files for environment variables
echo "GOOGLE_API_KEY=${GOOGLE_API_KEY}" > ./gemini-proxy/.env
echo "TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}" > ./telegram-bot/.env

# Run Docker Compose
docker-compose up --build


