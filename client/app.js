let socket;
let username;
let currentRoom = null;

// ===== CONECTAR =====
function connect() {
    username = document.getElementById("username").value.trim();
    if (!username) return alert("Ingresa un nombre");

    socket = new WebSocket("ws://localhost:8000");

    socket.onopen = () => {
        socket.send(JSON.stringify({
            type: "connect",
            username
        }));

        document.getElementById("login").style.display = "none";
        document.getElementById("chat").style.display = "flex";
    };

    socket.onmessage = (event) => handleServerMessage(event.data);

    socket.onclose = () => {
        alert("Conexión perdida");
        location.reload();
    };
}

// ===== PROCESAR MENSAJES =====
function handleServerMessage(raw) {
    let data;
    try { data = JSON.parse(raw); } catch { return; }

    switch (data.type) {

        case "connected":
            addMessage(data.message, "system");
            requestRooms();
            break;

        case "notice":
            addMessage(" " + data.message, "system");
            break;

        case "message":
            if (data.room !== currentRoom) return;
            addMessage(`<b>${data.sender}:</b> ${data.message}`,
                data.sender === username ? "me" : "user"
            );
            break;

        case "rooms":
            updateRoomList(data.rooms);
            break;
    }
}

// ===== AGREGAR MENSAJE =====
function addMessage(html, type = "user") {
    const box = document.getElementById("messages");
    box.innerHTML += `<div class="msg ${type}">${html}</div>`;
    box.scrollTop = box.scrollHeight;
}

// ===== UNIRSE =====
function joinRoom() {
    const room = document.getElementById("room").value.trim();
    if (!room) return;
    joinSpecificRoom(room);
}

function joinSpecificRoom(room) {
    currentRoom = room;

    document.getElementById("messages").innerHTML = "";

    socket.send(JSON.stringify({
        type: "join",
        room
    }));

    addMessage(`Te uniste a la sala <b>${room}</b>`, "system");

    requestRooms();
}

// ===== LISTA DE SALAS =====
function requestRooms() {
    socket.send(JSON.stringify({
        type: "list_rooms"
    }));
}

// ===== ACTUALIZAR LISTA =====
function updateRoomList(rooms) {
    const list = document.getElementById("room-list");
    list.innerHTML = "";

    rooms.forEach(room => {
        const div = document.createElement("div");
        div.textContent = room;

        if (room === currentRoom)
            div.classList.add("active-room");

        div.onclick = () => joinSpecificRoom(room);

        list.appendChild(div);
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

// ===== ENTER PARA ENVIAR =====
document.addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
});
