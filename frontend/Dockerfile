# Устанавливаем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем supervisord
RUN apt-get update && apt-get install -y supervisor

# Копируем весь проект в контейнер
COPY . .

# Копируем конфигурационный файл supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Указываем команду для запуска supervisord
CMD ["/usr/bin/supervisord"]