from domain.room import Room

class ChatService:
    _instance = None

    def __init__(self):
        self.rooms = {}

    @staticmethod
    def get_instance():
        if ChatService._instance is None:
            ChatService._instance = ChatService()
        return ChatService._instance

    def join_room(self, room_name, user):
        if room_name not in self.rooms:
            self.rooms[room_name] = Room(room_name)

        room = self.rooms[room_name]
        room.add_user(user)
        return room
