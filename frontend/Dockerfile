# Устанавливаем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Указываем команду для запуска приложения
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]
