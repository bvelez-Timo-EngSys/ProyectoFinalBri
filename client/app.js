let socket;
let username;
let currentRoom = null;  // Sala en la que el usuario está actualmente

// ===== CONECTAR =====
function connect() {
    username = document.getElementById("username").value.trim();
    if (!username) return alert("Ingresa un nombre");

    socket = new WebSocket("ws://localhost:8000");

    socket.onopen = () => {
        console.log("Conectado al servidor");

        // Envío obligatorio según tu servidor
        socket.send(JSON.stringify({
            type: "connect",
            username
        }));

        document.getElementById("login").style.display = "none";
        document.getElementById("chat").style.display = "flex";
    };

    socket.onmessage = (event) => handleServerMessage(event.data);

    socket.onclose = () => {
        alert("Se perdio conexión con el servidor");
        location.reload();
    };
}

// ===== PROCESAR MENSAJES DEL SERVIDOR =====
function handleServerMessage(raw) {
    let data;
    try {
        data = JSON.parse(raw);
    } catch {
        return;
    }

    switch (data.type) {
        case "connected":
            addMessage(" " + data.message, "system");
            requestRooms();
            break;

        case "notice":
            addMessage(" " + data.message, "system");
            break;
        

        case "message":
            if (data.room !== currentRoom) return; // ignorar mensajes de otras salas
            addMessage(
                `<b>${data.sender}:</b> ${data.message}`,
                data.sender === username ? "me" : "user"
            );
            break;

        case "rooms":
            updateRoomList(data.rooms);
            break;

        case "user_list":
            // Puedes mostrarla si quieres
            console.log("Usuarios en sala:", data.users);
            break;

        default:
            console.log("Mensaje desconocido:", data);
    }
}

// ===== AGREGAR MENSAJE AL CHAT =====
function addMessage(html, type = "user") {
    const box = document.getElementById("messages");

    box.innerHTML += `<div class="msg ${type}">${html}</div>`;
    box.scrollTop = box.scrollHeight;
}

// ===== UNIRSE A UNA SALA =====
function joinRoom() {
    const room = document.getElementById("room").value.trim();
    if (!room) return;
    joinSpecificRoom(room);
}

function joinSpecificRoom(roomName) {
    currentRoom = roomName;

    // Limpiar mensajes de la sala anterior
    document.getElementById("messages").innerHTML = "";

    socket.send(JSON.stringify({
        type: "join",
        room: roomName
    }));

    addMessage(` Te uniste a la sala: <b>${roomName}</b>`, "system");

    requestRooms();
}

// ===== SOLICITAR LISTA DE SALAS =====
function requestRooms() {
    socket.send(JSON.stringify({
        type: "list_rooms"
    }));
}

// ===== ACTUALIZAR LISTA DE SALAS =====
function updateRoomList(rooms) {
    const container = document.getElementById("room-list");
    container.innerHTML = "";

    rooms.forEach(room => {
        const div = document.createElement("div");
        div.classList.add("room-item");
        div.textContent = room;

        if (room === currentRoom)
            div.classList.add("active-room");

        div.onclick = () => joinSpecificRoom(room);

        container.appendChild(div);
    });
}

// ===== ENVIAR MENSAJE =====
function sendMessage() {
    const input = document.getElementById("msg");
    const text = input.value.trim();
    if (!text) return;

    socket.send(JSON.stringify({
        type: "message",
        message: text
    }));

    input.value = "";
}
