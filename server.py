import os
import queue
import json
import vosk
import sys
import sounddevice as sd
import asyncio
import websockets

# Загружаем Vosk-модель
MODEL_PATH = "model"
model = vosk.Model(MODEL_PATH)

# Очередь для потокового ввода аудио
q = queue.Queue()

# Настройки микрофона
SAMPLE_RATE = 16000
DEVICE = None  # Используем устройство по умолчанию

# Функция обработки входного аудиопотока
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

async def recognize(websocket, path):
    """Потоковое распознавание аудио из микрофона через WebSocket"""
    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetMaxAlternatives(1)
    rec.SetWords(True)

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, 
                           device=DEVICE, dtype="int16", channels=1, 
                           callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                await websocket.send(json.dumps(result))
            else:
                partial_result = json.loads(rec.PartialResult())
                await websocket.send(json.dumps(partial_result))

# Запуск WebSocket сервера
start_server = websockets.serve(recognize, "0.0.0.0", 2700)

print("WebSocket STT сервер запущен на ws://0.0.0.0:2700")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
