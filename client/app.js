let socket;
let username;

// --- conexión inicial ---
function connect() {
    username = document.getElementById("username").value.trim();

    if (!username) {
        alert("Debes ingresar un nombre");
        return;
    }

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
}

// --- manejar mensajes del servidor ---
function handleServerMessage(raw) {
    let data;

    try { data = JSON.parse(raw); }
    catch { return; }

    switch (data.type) {

        case "notice":
            addMessage(" " + data.message, "system");
            break;

        case "message":
            let css = data.sender === username ? "me" : "user";
            addMessage(`<b>${data.sender}:</b> ${data.message}`, css);
            break;

        case "rooms":
            updateRoomList(data.rooms);
            break;

        case "user_list":
            console.log("Usuarios en sala:", data.users);
            break;

        case "connected":
            addMessage(data.message, "system");
            requestRooms();
            break;
    }
}

// --- UI: agregar mensaje ---
function addMessage(html, type="user") {
    const msgBox = document.getElementById("messages");
    msgBox.innerHTML += `<div class="msg ${type}">${html}</div>`;
    msgBox.scrollTop = msgBox.scrollHeight;
}

// --- solicitar lista de salas ---
function requestRooms() {
    socket.send(JSON.stringify({ type: "list_rooms" }));
}

// --- UI: actualizar lista de salas ---
function updateRoomList(rooms) {
    const box = document.getElementById("room-list");
    box.innerHTML = "";

    rooms.forEach(r => {
        const div = document.createElement("div");
        div.textContent = r;
        div.onclick = () => joinSpecificRoom(r);
        box.appendChild(div);
    });
}

// --- unirse a sala desde input ---
function joinRoom() {
    const room = document.getElementById("room").value.trim();
    if (!room) return;
    joinSpecificRoom(room);
}

// --- unirse a sala específica ---
function joinSpecificRoom(room) {
    socket.send(JSON.stringify({
        type: "join",
        room
    }));
    addMessage(`Entraste a: ${room}`, "system");
    requestRooms();
}

// --- enviar mensaje ---
function sendMessage() {
    const msg = document.getElementById("msg").value.trim();
    if (!msg) return;

    socket.send(JSON.stringify({
        type: "message",
        message: msg
    }));

    document.getElementById("msg").value = "";
}
