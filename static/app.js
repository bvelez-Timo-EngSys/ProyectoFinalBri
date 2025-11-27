/**
 * Aplicación Cliente de Chat Colaborativo
 * Gestiona la conexión WebSocket y la interfaz de usuario
 */

class ChatApp {
    constructor() {
        this.ws = null;
        this.nombreUsuario = '';
        this.salaActual = '';
        this.inicializarEventos();
    }

    /**
     * Inicializa los event listeners
     */
    inicializarEventos() {
        // Enter para enviar mensaje
        document.getElementById('mensajeInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.enviarMensaje();
        });

        // Enter para conectar
        document.getElementById('nombreUsuario').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.conectar();
        });

        // Enter para crear sala
        document.getElementById('nombreSala').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.crearSala();
        });
    }

    /**
     * Conecta al servidor WebSocket
     */
    conectar() {
        this.nombreUsuario = document.getElementById('nombreUsuario').value.trim();
        
        if (!this.nombreUsuario) {
            alert('Por favor ingresa tu nombre');
            return;
        }

        // Determinar protocolo WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log(' Conectado al servidor');
            this.ws.send(JSON.stringify({
                tipo: 'conectar',
                nombre: this.nombreUsuario
            }));
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.manejarMensaje(data);
        };

        this.ws.onerror = (error) => {
            console.error('Error de conexión:', error);
            alert('Error de conexión con el servidor');
        };

        this.ws.onclose = () => {
            console.log(' Conexión cerrada');
            alert('Conexión cerrada. Recarga la página para reconectar.');
        };
    }

    /**
     * Maneja los mensajes recibidos del servidor
     */
    manejarMensaje(data) {
        console.log(' Mensaje recibido:', data.tipo);

        switch (data.tipo) {
            case 'conectado':
                this.mostrarPanelPrincipal();
                break;

            case 'salas_disponibles':
                this.mostrarSalas(data.salas);
                break;

            case 'sala_unida':
                this.salaActual = data.sala;
                document.getElementById('salaActual').textContent = data.sala;
                document.getElementById('chatMensajes').innerHTML = '';
                this.actualizarUsuarios(data.usuarios);
                break;

            case 'mensaje':
                this.agregarMensaje(data);
                break;

            case 'usuario_entro':
                this.agregarMensajeSistema(`${data.nombre} se unió a la sala`);
                this.actualizarUsuarios(data.usuarios);
                break;

            case 'usuario_salio':
                this.agregarMensajeSistema(`${data.nombre} salió de la sala`);
                break;

            case 'error':
                alert(data.mensaje);
                break;

            default:
                console.warn('Tipo de mensaje desconocido:', data.tipo);
        }
    }

    /**
     * Muestra el panel principal (salas y chat)
     */
    mostrarPanelPrincipal() {
        document.getElementById('loginPanel').classList.add('hidden');
        document.getElementById('salasPanel').classList.remove('hidden');
        document.getElementById('chatPanel').classList.remove('hidden');
    }

    /**
     * Muestra la lista de salas disponibles
     */
    mostrarSalas(salas) {
        const lista = document.getElementById('salasLista');
        lista.innerHTML = '';

        if (salas.length === 0) {
            lista.innerHTML = '<p style="padding: 20px; text-align: center; color: #999;">No hay salas disponibles. ¡Crea una!</p>';
            return;
        }

        salas.forEach(sala => {
            const div = document.createElement('div');
            div.className = 'sala-item';
            
            if (sala.nombre === this.salaActual) {
                div.classList.add('activa');
            }

            div.innerHTML = `
                <div class="sala-nombre">${this.escaparHTML(sala.nombre)}</div>
                <div class="sala-usuarios">
                    👥 ${sala.usuarios} usuario(s)
                </div>
            `;

            div.onclick = () => this.unirseASala(sala.nombre);
            lista.appendChild(div);
        });
    }

    /**
     * Crea una nueva sala
     */
    crearSala() {
        const nombreSala = document.getElementById('nombreSala').value.trim();
        
        if (!nombreSala) {
            alert('Ingresa un nombre para la sala');
            return;
        }

        this.ws.send(JSON.stringify({
            tipo: 'crear_sala',
            nombre_sala: nombreSala
        }));

        document.getElementById('nombreSala').value = '';
    }

    /**
     * Se une a una sala existente
     */
    unirseASala(nombreSala) {
        if (nombreSala === this.salaActual) {
            return; // Ya está en esta sala
        }

        this.ws.send(JSON.stringify({
            tipo: 'unirse_sala',
            nombre_sala: nombreSala
        }));
    }

    /**
     * Envía un mensaje a la sala actual
     */
    enviarMensaje() {
        const input = document.getElementById('mensajeInput');
        const contenido = input.value.trim();

        if (!contenido || !this.salaActual) {
            return;
        }

        this.ws.send(JSON.stringify({
            tipo: 'mensaje',
            contenido: contenido
        }));

        input.value = '';
        input.focus();
    }

    /**
     * Agrega un mensaje al chat
     */
    agregarMensaje(data) {
        const mensajes = document.getElementById('chatMensajes');
        const div = document.createElement('div');
        div.className = 'mensaje';

        const tiempo = new Date(data.timestamp).toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });

        div.innerHTML = `
            <div class="mensaje-header">
                <span class="mensaje-autor">${this.escaparHTML(data.nombre)}</span>
                <span class="mensaje-tiempo">${tiempo}</span>
            </div>
            <div class="mensaje-contenido">${this.escaparHTML(data.contenido)}</div>
        `;

        mensajes.appendChild(div);
        this.scrollAlFinal(mensajes);
    }

    /**
     * Agrega un mensaje del sistema
     */
    agregarMensajeSistema(texto) {
        const mensajes = document.getElementById('chatMensajes');
        const div = document.createElement('div');
        div.className = 'mensaje mensaje-sistema';
        div.textContent = texto;
        mensajes.appendChild(div);
        this.scrollAlFinal(mensajes);
    }

    /**
     * Actualiza la lista de usuarios conectados
     */
    actualizarUsuarios(usuarios) {
        const div = document.getElementById('usuariosConectados');
        div.textContent = `👥 ${usuarios.join(', ')}`;
    }

    /**
     * Hace scroll al final del contenedor
     */
    scrollAlFinal(elemento) {
        elemento.scrollTop = elemento.scrollHeight;
    }

    /**
     * Escapa HTML para prevenir XSS
     */
    escaparHTML(texto) {
        const div = document.createElement('div');
        div.textContent = texto;
        return div.innerHTML;
    }
}

// Inicializar aplicación cuando cargue el DOM
const app = new ChatApp();
console.log(' Chat App iniciada');