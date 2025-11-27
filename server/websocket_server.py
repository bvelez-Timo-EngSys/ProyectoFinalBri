import json
import asyncio
import websockets
from domain.user import User
from services.chat_service import ChatService
from infrastructure.utils import sanitize_name, timestamp_now, broadcast_json

chat = ChatService.get_instance()

async def notify_room_userlist(room):
    users = [{"name": u.name} for u in room.users]
    await broadcast_json(room.users, {
        "type": "user_list",
        "room": room.name,
        "users": users,
        "timestamp": timestamp_now()
    })

async def handler(websocket):
    user = None
    current_room = None

    try:
        async for raw in websocket:
            try:
                data = json.loads(raw)
            except Exception:
                await websocket.send(json.dumps({"type": "error", "message": "JSON inválido"}))
                continue

            t = data.get("type")

            if t == "connect":
                name = sanitize_name(data.get("username", ""))
                if not name:
                    await websocket.send(json.dumps({"type": "error", "message": "Nombre vacío"}))
                    continue
                user = User(name, websocket)
                await websocket.send(json.dumps({"type": "connected", "message": f"Bienvenido, {name}"}))

            elif t == "join":
                if not user:
                    await websocket.send(json.dumps({"type": "error", "message": "No conectado"}))
                    continue

                room_name = sanitize_name(data.get("room", "general"))

                if current_room:
                    current_room.remove_user(user)
                    await broadcast_json(current_room.users, {
                        "type": "notice",
                        "message": f"{user.name} salió de la sala."
                    })
                    await notify_room_userlist(current_room)

                room = chat.join_room(room_name, user)
                current_room = room

                await broadcast_json(room.users, {
                    "type": "notice",
                    "message": f"{user.name} se unió a la sala."
                })
                await notify_room_userlist(room)

            elif t == "message":
                if not user or not current_room:
                    await websocket.send(json.dumps({"type": "error", "message": "No está en ninguna sala"}))
                    continue

                text = data.get("message", "").strip()
                if not text:
                    continue

                payload = {
                    "type": "message",
                    "room": current_room.name,
                    "sender": user.name,
                    "message": text,
                    "timestamp": timestamp_now()
                }
                await broadcast_json(current_room.users, payload)

            elif t == "leave":
                if user and current_room:
                    current_room.remove_user(user)
                    await broadcast_json(current_room.users, {
                        "type": "notice",
                        "message": f"{user.name} salió de la sala."
                    })
                    await notify_room_userlist(current_room)
                    current_room = None

            elif t == "list_rooms":
                rooms = list(chat.rooms.keys())
                await websocket.send(json.dumps({"type": "rooms", "rooms": rooms}))

            else:
                await websocket.send(json.dumps({"type": "error", "message": "Tipo desconocido"}))

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        if user and current_room:
            try:
                current_room.remove_user(user)
            except:
                pass
            await broadcast_json(current_room.users,
                {"type": "notice", "message": f"{user.name} se desconectó."})
            await notify_room_userlist(current_room)
