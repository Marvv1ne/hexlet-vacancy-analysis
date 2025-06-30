# Используем официальный Python-образ
FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /code

# Копируем зависимости
COPY requirements.txt ./
COPY pyproject.toml ./

# Устанавливаем зависимости
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r pyproject.toml || true

# Копируем проект
COPY . .

# Собираем статику (на всякий случай)
RUN python manage.py collectstatic --noinput || true

# Открываем порт для Django
EXPOSE 8000

# По умолчанию запускаем сервер (может быть переопределено в docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 