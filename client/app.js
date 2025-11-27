let socket;
let username;

function connect() {
    username = document.getElementById("username").value;

    socket = new WebSocket("ws://localhost:8000");

    socket.onopen = () => {
        socket.send(JSON.stringify({
            type: "connect",
            username
        }));

        document.getElementById("login").style.display = "none";
        document.getElementById("chat").style.display = "block";
    };

    socket.onmessage = (event) => {
        const msgBox = document.getElementById("messages");
        msgBox.innerHTML += `<p>${event.data}</p>`;
        msgBox.scrollTop = msgBox.scrollHeight;
    };
}

function joinRoom() {
    const room = document.getElementById("room").value;

    socket.send(JSON.stringify({
        type: "join",
        room
    }));
}

function sendMessage() {
    const msg = document.getElementById("msg").value;

    socket.send(JSON.stringify({
        type: "message",
        message: msg
    }));
}
