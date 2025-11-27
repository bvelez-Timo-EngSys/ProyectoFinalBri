import asyncio
import websockets
from websocket_server import handler

HOST = "localhost"
PORT = 8000

async def main():
    print(f"Servidor WebSocket iniciado en ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()  # servidor infinito

if __name__ == "__main__":
    asyncio.run(main())
