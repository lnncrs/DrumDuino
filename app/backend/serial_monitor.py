"""Monitor serial do DrumDuino: uv run python -m app.backend.serial_monitor."""

import argparse
from datetime import datetime
import sys

import serial
from serial.tools import list_ports


def positive_integer(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("Informe um número maior que zero.")
    return number


def monitor(connection: serial.Serial) -> None:
    """Acumula bytes até uma linha completa, mesmo entre timeouts."""
    pending = bytearray()
    while True:
        chunk = connection.read_until(b"\n", size=4096)
        if not chunk:
            continue
        pending.extend(chunk)
        while b"\n" in pending:
            line, _, remainder = pending.partition(b"\n")
            pending = bytearray(remainder)
            message = line.rstrip(b"\r").decode("utf-8", errors="replace")
            print(f"[{datetime.now():%H:%M:%S}] {message}", flush=True)
        if len(pending) > 16384:
            print("Aviso: dados sem quebra de linha descartados.", file=sys.stderr)
            pending.clear()


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor serial do DrumDuino")
    parser.add_argument(
        "--list-ports", action="store_true", help="Listar portas disponíveis"
    )
    parser.add_argument("--port", help="Porta do Nano, como COM3 ou /dev/ttyUSB0")
    parser.add_argument(
        "--baud",
        type=positive_integer,
        default=9600,
        help="Velocidade serial (padrão: 9600)",
    )
    args = parser.parse_args()

    if args.list_ports:
        ports = sorted(list_ports.comports(), key=lambda port: port.device)
        for port in ports:
            print(f"{port.device}: {port.description}")
        if not ports:
            print("Nenhuma porta serial encontrada.")
        return 0

    if not args.port:
        parser.error("Use --list-ports ou informe --port.")

    try:
        with serial.Serial(args.port, args.baud, timeout=0.2) as connection:
            print(
                f"Conectado a {args.port} em {args.baud} baud. Ctrl+C para sair.",
                flush=True,
            )
            print("A abertura da porta pode reiniciar o Nano.", flush=True)
            monitor(connection)
    except KeyboardInterrupt:
        print("\nMonitor encerrado.")
        return 0
    except (serial.SerialException, OSError) as error:
        print(f"Erro serial: {error}", file=sys.stderr)
        print(
            "Confira a conexão e feche outros programas que usam a porta.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
