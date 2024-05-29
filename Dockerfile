# Используйте официальный образ Python как базовый
FROM python:3.9-slim

# Установите рабочий каталог в контейнере
WORKDIR /app

# Скопируйте файлы зависимостей в рабочую директорию
COPY requirements.txt .

# Установите зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте остальные файлы проекта в рабочую директорию
COPY . .

# Задайте переменные окружения
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Объявите порт, который будет слушать сервер
EXPOSE 5000

# Команда для запуска приложения
CMD ["python", "-m", "app", "run"]