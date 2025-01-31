# Используем образ Python 3.10
FROM python:3.10

WORKDIR /app

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    wget unzip portaudio19-dev && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем Vosk и WebSockets
RUN pip install vosk sounddevice websockets flask

# Загружаем маленькую русскую модель Vosk
RUN wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip && \
    unzip vosk-model-small-ru-0.22.zip && \
    mv vosk-model-small-ru-0.22 model && \
    rm vosk-model-small-ru-0.22.zip

# Копируем серверный скрипт
COPY server.py /app/server.py

# Открываем порты и запускаем сервер
EXPOSE 2700
CMD ["python3", "server.py"]
