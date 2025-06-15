import uvicorn, serial
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import threading
import time
import socket

app = FastAPI()

SERIAL_PORT = 'COM3' # Change this to your serial port of the Arduino
BAUD_RATE = 9600

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

@app.get("/")
def read_root():
    return PlainTextResponse("Connection Working", 200)

@app.get("/damage")
def take_damage(time: int | None = None):
    if time is None:
        return PlainTextResponse("No damage value entered", 200)
    elif time < 0:
        return PlainTextResponse("Damage value cannot be negative", 400)
    else:
        ser.write(f"{time}\n".encode())
        return PlainTextResponse(f"Damage taken: {time} seconds", 200)
    
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == "__main__":
    local_ip = get_local_ip()
    uvicorn.run(app, host=local_ip, port=8000)