# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt в рабочую директорию
COPY requirements.txt .

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в рабочую директорию
COPY . .

# Запускаем приложение
CMD ["python", "bot.py"]

