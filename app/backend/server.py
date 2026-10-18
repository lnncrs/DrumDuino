"""Servidor local: uv run python -m app.backend.server."""

import asyncio
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import serial
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from serial.tools import list_ports

from app.backend import config
from app.backend.audio import Audio

frontend = Path(__file__).resolve().parents[1] / "frontend"
connection = None
messages = deque(maxlen=500)
sequence = 0
error = ""
lock = asyncio.Lock()
audio = Audio()


def record(text):
    global sequence
    sequence += 1
    messages.append(
        {"id": sequence, "time": datetime.now().strftime("%H:%M:%S"), "text": text}
    )


def disconnect():
    global connection
    if connection is not None:
        connection.close()
        connection = None


async def read_serial():
    global error
    pending = bytearray()
    previous = None
    while True:
        async with lock:
            if connection is not previous:
                pending.clear()
                previous = connection
            if connection is not None:
                try:
                    # Leitura sem espera: a atualização da página não controla o sensor.
                    pending.extend(connection.read(min(connection.in_waiting, 4096)))
                    while b"\n" in pending:
                        line, _, pending = pending.partition(b"\n")
                        message = line.rstrip(b"\r").decode("utf-8", errors="replace")
                        record(message)
                        note = audio.hit(message)
                        if note is not None:
                            asyncio.get_running_loop().call_later(
                                0.08, audio.stop_note, note
                            )
                    if len(pending) > 16384:
                        pending.clear()
                        record("Aviso: dados sem quebra de linha descartados.")
                except (serial.SerialException, OSError) as exc:
                    error = f"Conexão interrompida: {exc}"
                    disconnect()
        await asyncio.sleep(0.02)


@asynccontextmanager
async def lifespan(app):
    await asyncio.to_thread(audio.start)
    task = asyncio.create_task(read_serial())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        disconnect()
        audio.close()


app = FastAPI(lifespan=lifespan)
app.state.fluidsynth_dll = config.FLUIDSYNTH_DLL
app.state.soundfont = config.SOUNDFONT
app.mount("/static", StaticFiles(directory=frontend), name="static")


class Settings(BaseModel):
    port: str
    baud: int = Field(default=9600, ge=300, le=2000000)


@app.middleware("http")
async def local_requests(request: Request, call_next):
    # Comandos de conexão devem vir da própria página local.
    if request.method == "POST" and request.headers.get("origin") != str(
        request.base_url
    ).rstrip("/"):
        from fastapi.responses import JSONResponse

        return JSONResponse(
            {"detail": "Abra a interface pelo endereço local do servidor."},
            status_code=403,
        )
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def index():
    return FileResponse(frontend / "index.html")


@app.get("/api/ports")
def ports():
    return [{"port": p.device, "name": p.description} for p in list_ports.comports()]


@app.get("/api/state")
async def state(after: int = 0):
    return {
        "port": connection.port if connection else None,
        "error": error,
        "audio": audio.status(),
        "total": sequence,
        "messages": [m for m in messages if m["id"] > after],
    }


@app.post("/api/connect")
async def connect(settings: Settings):
    global connection, error
    async with lock:
        if connection:
            raise HTTPException(409, "Desconecte a placa antes de trocar a conexão.")
        if settings.port not in [p.device for p in list_ports.comports()]:
            raise HTTPException(400, "Porta não encontrada. Atualize a lista.")
        try:
            connection = await asyncio.to_thread(
                serial.Serial, settings.port, settings.baud, timeout=0
            )
        except (serial.SerialException, OSError) as exc:
            raise HTTPException(
                400,
                "Não foi possível abrir a porta. Feche os outros monitores e confira a placa.",
            ) from exc
        error = ""
    return {"connected": True}


@app.post("/api/disconnect")
async def close():
    async with lock:
        disconnect()
    return {"connected": False}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
