# Устанавливаем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install -r requirements.txt

RUN pip install aiofiles==23.2.1

# Копируем весь проект в контейнер
COPY . .

# Указываем команду для запуска приложения
CMD ["python3", "main.py"]

