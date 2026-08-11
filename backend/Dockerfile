FROM python:3.11-slim

# Установка системных зависимостей (Mesh/Blender библиотеки)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    blender \
    && rm -rf /var/lib/apt/lists/*

# Установка пакетного менеджера uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml ./
RUN uv pip install --system -e .[dev]

# Копирование исходного кода
COPY . .

# Генерация Prisma-клиента
RUN python -m prisma generate || true

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
