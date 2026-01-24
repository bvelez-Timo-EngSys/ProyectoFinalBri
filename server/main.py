import asyncio
import websockets
from websocket_server import handler

HOST = "10.253.3.6"
PORT = 8000

async def main():
    print(f"Servidor WebSocket iniciado en ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()  # servidor infinito

if __name__ == "__main__":
    asyncio.run(main())
