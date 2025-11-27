"""
Servidor de Chat Colaborativo con Salas Temáticas
Implementación con Patrones de Diseño: Creacionales, Estructurales y de Comportamiento
CON LOGGING DETALLADO PARA VISUALIZAR INTERACCIONES
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import os
import logging
from colorama import Fore, Back, Style, init

# Inicializar colorama para colores en consola
init(autoreset=True)

# Configurar logging personalizado
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# ===========================
# UTILIDADES DE LOGGING
# ===========================

class ConsoleLogger:
    """Clase para logging con colores y formato mejorado"""
    
    @staticmethod
    def patron(nombre_patron: str, accion: str, detalles: str = ""):
        """Log de patrones de diseño"""
        # Deshabilitado - no mostrar información de patrones
        pass
    
    @staticmethod
    def websocket(accion: str, usuario: str = "", sala: str = "", extra: str = ""):
        """Log de eventos WebSocket"""
        print(f"{Fore.MAGENTA} WebSocket | {accion}")
        if usuario:
            print(f"    Usuario: {usuario}")
        if sala:
            print(f"    Sala: {sala}")
        if extra:
            print(f"     {extra}")
    
    @staticmethod
    def mensaje(tipo: str, emisor: str, contenido: str, sala: str):
        """Log de mensajes de chat"""
        print(f"{Fore.BLUE} MENSAJE [{tipo}]")
        print(f"    De: {emisor}")
        print(f"    En: {sala}")
        print(f"    Contenido: {contenido[:50]}...")
    
    @staticmethod
    def estado(titulo: str, datos: Dict[str, Any]):
        """Log del estado del sistema"""
        print(f"\n{Fore.GREEN}{'='*80}")
        print(f"{Fore.WHITE} ESTADO DEL SISTEMA: {titulo}")
        for key, value in datos.items():
            print(f"    {key}: {value}")
        print(f"{Fore.GREEN}{'='*80}\n")
    
    @staticmethod
    def error(mensaje: str, detalles: str = ""):
        """Log de errores"""
        print(f"{Fore.RED} ERROR: {mensaje}")
        if detalles:
            print(f"   {detalles}")

# ===========================
# PATRONES CREACIONALES
# ===========================

#  PATRÓN SINGLETON - Asegura una única instancia del gestor de chat
class SingletonMeta(type):
    """Metaclase que implementa el patrón Singleton"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            ConsoleLogger.patron(
                "SINGLETON",
                "Creando PRIMERA instancia",
                f"Clase: {cls.__name__}"
            )
            cls._instances[cls] = super().__call__(*args, **kwargs)
        else:
            ConsoleLogger.patron(
                "SINGLETON",
                "Retornando instancia existente",
                f"Clase: {cls.__name__}"
            )
        return cls._instances[cls]


#  PATRÓN FACTORY METHOD - Crea diferentes tipos de mensajes
class Mensaje(ABC):
    """Clase base abstracta para todos los tipos de mensajes"""
    
    def __init__(self, nombre: str, timestamp: str):
        self.nombre = nombre
        self.timestamp = timestamp
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el mensaje a diccionario para envío"""
        pass


class MensajeChat(Mensaje):
    """Mensaje de chat normal"""
    
    def __init__(self, nombre: str, contenido: str, timestamp: str):
        super().__init__(nombre, timestamp)
        self.contenido = contenido
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tipo": "mensaje",
            "nombre": self.nombre,
            "contenido": self.contenido,
            "timestamp": self.timestamp
        }


class MensajeSistema(Mensaje):
    """Mensaje del sistema (usuario entró/salió)"""
    
    def __init__(self, nombre: str, accion: str, timestamp: str, usuarios: List[str] = None):
        super().__init__(nombre, timestamp)
        self.accion = accion
        self.usuarios = usuarios or []
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "tipo": self.accion,
            "nombre": self.nombre,
            "timestamp": self.timestamp
        }
        if self.usuarios:
            data["usuarios"] = self.usuarios
        return data


class MensajeFactory:
    """ FACTORY METHOD - Crea instancias de diferentes tipos de mensajes"""
    
    @staticmethod
    def crear_mensaje_chat(nombre: str, contenido: str) -> MensajeChat:
        ConsoleLogger.patron(
            "FACTORY METHOD",
            "Creando MensajeChat",
            f"Usuario: {nombre} | Contenido: {contenido[:30]}..."
        )
        return MensajeChat(nombre, contenido, datetime.now().isoformat())
    
    @staticmethod
    def crear_mensaje_entrada(nombre: str, usuarios: List[str]) -> MensajeSistema:
        ConsoleLogger.patron(
            "FACTORY METHOD",
            "Creando MensajeSistema (ENTRADA)",
            f"Usuario: {nombre} | Total usuarios en sala: {len(usuarios)}"
        )
        return MensajeSistema(nombre, "usuario_entro", datetime.now().isoformat(), usuarios)
    
    @staticmethod
    def crear_mensaje_salida(nombre: str) -> MensajeSistema:
        ConsoleLogger.patron(
            "FACTORY METHOD",
            "Creando MensajeSistema (SALIDA)",
            f"Usuario: {nombre}"
        )
        return MensajeSistema(nombre, "usuario_salio", datetime.now().isoformat())


#  PATRÓN BUILDER - Construye objetos Sala de manera fluida
class Sala:
    """Representa una sala de chat"""
    
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.usuarios: Dict[str, WebSocket] = {}
        self.creada_en = datetime.now().isoformat()
        ConsoleLogger.websocket(
            "Sala creada",
            sala=nombre,
            extra=f"Timestamp: {self.creada_en}"
        )
    
    def agregar_usuario(self, nombre: str, websocket: WebSocket):
        self.usuarios[nombre] = websocket
        ConsoleLogger.websocket(
            "Usuario agregado a sala",
            usuario=nombre,
            sala=self.nombre,
            extra=f"Total usuarios: {len(self.usuarios)}"
        )
    
    def remover_usuario(self, nombre: str):
        if nombre in self.usuarios:
            self.usuarios.pop(nombre)
            ConsoleLogger.websocket(
                "Usuario removido de sala",
                usuario=nombre,
                sala=self.nombre,
                extra=f"Usuarios restantes: {len(self.usuarios)}"
            )
    
    def obtener_nombres_usuarios(self) -> List[str]:
        return list(self.usuarios.keys())
    
    def obtener_websockets(self) -> List[WebSocket]:
        return list(self.usuarios.values())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "usuarios": len(self.usuarios),
            "creada_en": self.creada_en
        }


class SalaBuilder:
    """ BUILDER - Construye objetos Sala paso a paso"""
    
    def __init__(self):
        self._sala: Optional[Sala] = None
    
    def crear_nueva(self, nombre: str) -> 'SalaBuilder':
        ConsoleLogger.patron(
            "BUILDER",
            "Iniciando construcción de Sala",
            f"Nombre: {nombre}"
        )
        self._sala = Sala(nombre)
        return self
    
    def agregar_usuario_inicial(self, nombre: str, websocket: WebSocket) -> 'SalaBuilder':
        if self._sala:
            ConsoleLogger.patron(
                "BUILDER",
                "Agregando usuario inicial",
                f"Usuario: {nombre}"
            )
            self._sala.agregar_usuario(nombre, websocket)
        return self
    
    def build(self) -> Sala:
        ConsoleLogger.patron(
            "BUILDER",
            "Finalizando construcción de Sala",
            f"Sala completada: {self._sala.nombre if self._sala else 'None'}"
        )
        sala = self._sala
        self._sala = None
        return sala


# ===========================
# PATRONES ESTRUCTURALES
# ===========================

#  PATRÓN FACADE - Simplifica la interfaz del sistema de chat
class ChatFacade(metaclass=SingletonMeta):
    """ FACADE - Proporciona una interfaz simplificada para operaciones complejas"""
    
    def __init__(self):
        self.salas: Dict[str, Sala] = {}
        self.conexiones: Dict[WebSocket, str] = {}
        self.usuarios_salas: Dict[WebSocket, str] = {}
        self._builder = SalaBuilder()
        ConsoleLogger.patron(
            "FACADE",
            "ChatFacade inicializado",
            "Sistema de gestión de chat listo"
        )
    
    def crear_sala(self, nombre_sala: str) -> bool:
        """Crea una nueva sala si no existe"""
        ConsoleLogger.patron(
            "FACADE",
            "Intentando crear sala",
            f"Nombre: {nombre_sala}"
        )
        
        if nombre_sala in self.salas:
            ConsoleLogger.error(f"Sala '{nombre_sala}' ya existe")
            return False
        
        sala = self._builder.crear_nueva(nombre_sala).build()
        self.salas[nombre_sala] = sala
        
        ConsoleLogger.patron(
            "FACADE",
            "Sala creada exitosamente",
            f"Total salas activas: {len(self.salas)}"
        )
        return True
    
    def unir_usuario_a_sala(self, websocket: WebSocket, nombre_usuario: str, nombre_sala: str):
        """Une un usuario a una sala específica"""
        ConsoleLogger.patron(
            "FACADE",
            "Uniendo usuario a sala",
            f"Usuario: {nombre_usuario} → Sala: {nombre_sala}"
        )
        
        if nombre_sala not in self.salas:
            self.salas[nombre_sala] = Sala(nombre_sala)
        
        sala = self.salas[nombre_sala]
        sala.agregar_usuario(nombre_usuario, websocket)
        
        self.conexiones[websocket] = nombre_usuario
        self.usuarios_salas[websocket] = nombre_sala
        
        self._mostrar_estado()
    
    def obtener_sala_usuario(self, websocket: WebSocket) -> Optional[str]:
        """Obtiene la sala en la que está un usuario"""
        return self.usuarios_salas.get(websocket)
    
    def obtener_usuarios_de_sala(self, nombre_sala: str) -> List[str]:
        """Obtiene lista de usuarios en una sala"""
        sala = self.salas.get(nombre_sala)
        usuarios = sala.obtener_nombres_usuarios() if sala else []
        
        ConsoleLogger.patron(
            "FACADE",
            "Consultando usuarios de sala",
            f"Sala: {nombre_sala} | Usuarios: {usuarios}"
        )
        return usuarios
    
    def desconectar_usuario(self, websocket: WebSocket):
        """Desconecta un usuario y lo remueve de su sala"""
        nombre_sala = self.usuarios_salas.get(websocket)
        nombre_usuario = self.conexiones.get(websocket)
        
        ConsoleLogger.patron(
            "FACADE",
            "Desconectando usuario",
            f"Usuario: {nombre_usuario} | Sala: {nombre_sala}"
        )
        
        if nombre_sala and nombre_sala in self.salas:
            sala = self.salas[nombre_sala]
            if nombre_usuario:
                sala.remover_usuario(nombre_usuario)
            
            if len(sala.usuarios) == 0:
                ConsoleLogger.patron(
                    "FACADE",
                    "Eliminando sala vacía",
                    f"Sala: {nombre_sala}"
                )
                del self.salas[nombre_sala]
        
        self.conexiones.pop(websocket, None)
        self.usuarios_salas.pop(websocket, None)
        
        self._mostrar_estado()
    
    def obtener_info_salas(self) -> List[Dict[str, Any]]:
        """Obtiene información de todas las salas disponibles"""
        return [sala.to_dict() for sala in self.salas.values()]
    
    def _mostrar_estado(self):
        """Muestra el estado actual del sistema"""
        ConsoleLogger.estado(
            "Estado Actual",
            {
                "Salas activas": len(self.salas),
                "Usuarios conectados": len(self.conexiones),
                "Salas": list(self.salas.keys())
            }
        )


#  PATRÓN ADAPTER - Adapta el formato de mensajes para WebSocket
class WebSocketAdapter:
    """ ADAPTER - Adapta objetos Mensaje para envío por WebSocket"""
    
    @staticmethod
    async def enviar_mensaje(websocket: WebSocket, mensaje: Mensaje):
        """Adapta y envía un mensaje a través de WebSocket"""
        ConsoleLogger.patron(
            "ADAPTER",
            "Adaptando Mensaje para WebSocket",
            f"Tipo: {type(mensaje).__name__}"
        )
        try:
            await websocket.send_json(mensaje.to_dict())
        except Exception as e:
            ConsoleLogger.error(f"Error al enviar mensaje", str(e))
    
    @staticmethod
    async def enviar_dict(websocket: WebSocket, data: Dict[str, Any]):
        """Envía un diccionario directamente"""
        ConsoleLogger.patron(
            "ADAPTER",
            "Enviando diccionario por WebSocket",
            f"Tipo mensaje: {data.get('tipo', 'desconocido')}"
        )
        try:
            await websocket.send_json(data)
        except Exception as e:
            ConsoleLogger.error(f"Error al enviar datos", str(e))


# ===========================
# PATRONES DE COMPORTAMIENTO
# ===========================

#  PATRÓN OBSERVER - Notifica a múltiples clientes sobre cambios
class Observador(ABC):
    """Interfaz base para observadores"""
    
    @abstractmethod
    async def actualizar(self, mensaje: Dict[str, Any]):
        pass


class WebSocketObservador(Observador):
    """ OBSERVER - Observador concreto que escucha cambios y notifica por WebSocket"""
    
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        ConsoleLogger.patron(
            "OBSERVER",
            "Observador WebSocket creado",
            "Listo para recibir notificaciones"
        )
    
    async def actualizar(self, mensaje: Dict[str, Any]):
        ConsoleLogger.patron(
            "OBSERVER",
            "Notificando a observador",
            f"Mensaje tipo: {mensaje.get('tipo')}"
        )
        await WebSocketAdapter.enviar_dict(self.websocket, mensaje)


class SalaObservable:
    """ OBSERVER - Sujeto observable que notifica a todos los observadores"""
    
    def __init__(self):
        self._observadores: List[Observador] = []
        ConsoleLogger.patron(
            "OBSERVER",
            "Sala Observable creada",
            "Lista de observadores inicializada"
        )
    
    def agregar_observador(self, observador: Observador):
        self._observadores.append(observador)
        ConsoleLogger.patron(
            "OBSERVER",
            "Observador agregado",
            f"Total observadores: {len(self._observadores)}"
        )
    
    def remover_observador(self, observador: Observador):
        self._observadores.remove(observador)
        ConsoleLogger.patron(
            "OBSERVER",
            "Observador removido",
            f"Observadores restantes: {len(self._observadores)}"
        )
    
    async def notificar(self, mensaje: Dict[str, Any]):
        ConsoleLogger.patron(
            "OBSERVER",
            "Notificando a todos los observadores",
            f"Total: {len(self._observadores)} observadores"
        )
        for observador in self._observadores[:]:
            try:
                await observador.actualizar(mensaje)
            except:
                pass


#  PATRÓN CHAIN OF RESPONSIBILITY - Maneja diferentes tipos de mensajes
class ManejadorMensaje(ABC):
    """ CHAIN OF RESPONSIBILITY - Clase base para cadena de manejo de mensajes"""
    
    def __init__(self):
        self._siguiente: Optional[ManejadorMensaje] = None
    
    def establecer_siguiente(self, manejador: 'ManejadorMensaje') -> 'ManejadorMensaje':
        self._siguiente = manejador
        ConsoleLogger.patron(
            "CHAIN OF RESPONSIBILITY",
            "Enlazando manejadores",
            f"{type(self).__name__} → {type(manejador).__name__}"
        )
        return manejador
    
    @abstractmethod
    async def manejar(self, websocket: WebSocket, data: Dict[str, Any], contexto: Dict[str, Any]) -> bool:
        """Retorna True si manejó el mensaje, False si debe pasar al siguiente"""
        pass


class ManejadorConectar(ManejadorMensaje):
    """Maneja mensajes de tipo 'conectar'"""
    
    async def manejar(self, websocket: WebSocket, data: Dict[str, Any], contexto: Dict[str, Any]) -> bool:
        tipo = data.get("tipo")
        ConsoleLogger.patron(
            "CHAIN OF RESPONSIBILITY",
            f"ManejadorConectar procesando mensaje",
            f"Tipo recibido: {tipo}"
        )
        
        if tipo != "conectar":
            print(f"{Fore.YELLOW}     Pasando al siguiente manejador...")
            return await self._siguiente.manejar(websocket, data, contexto) if self._siguiente else False
        
        nombre_usuario = data.get("nombre")
        contexto["usuario_actual"] = nombre_usuario
        
        ConsoleLogger.websocket(
            "NUEVA CONEXIÓN",
            usuario=nombre_usuario,
            extra="Usuario autenticado"
        )
        
        facade = ChatFacade()
        
        await WebSocketAdapter.enviar_dict(websocket, {
            "tipo": "conectado",
            "mensaje": f"Bienvenido {nombre_usuario}!"
        })
        
        salas = facade.obtener_info_salas()
        await WebSocketAdapter.enviar_dict(websocket, {
            "tipo": "salas_disponibles",
            "salas": salas
        })
        
        return True


class ManejadorCrearSala(ManejadorMensaje):
    """Maneja mensajes de tipo 'crear_sala'"""
    
    async def manejar(self, websocket: WebSocket, data: Dict[str, Any], contexto: Dict[str, Any]) -> bool:
        tipo = data.get("tipo")
        ConsoleLogger.patron(
            "CHAIN OF RESPONSIBILITY",
            f"ManejadorCrearSala procesando mensaje",
            f"Tipo recibido: {tipo}"
        )
        
        if tipo != "crear_sala":
            print(f"{Fore.YELLOW}     Pasando al siguiente manejador...")
            return await self._siguiente.manejar(websocket, data, contexto) if self._siguiente else False
        
        facade = ChatFacade()
        nombre_sala = data.get("nombre_sala")
        usuario_actual = contexto.get("usuario_actual")
        
        if facade.crear_sala(nombre_sala):
            facade.unir_usuario_a_sala(websocket, usuario_actual, nombre_sala)
            contexto["sala_actual"] = nombre_sala
            
            await WebSocketAdapter.enviar_dict(websocket, {
                "tipo": "sala_unida",
                "sala": nombre_sala,
                "usuarios": [usuario_actual]
            })
            
            await notificar_salas_globalmente()
        else:
            await WebSocketAdapter.enviar_dict(websocket, {
                "tipo": "error",
                "mensaje": "La sala ya existe"
            })
        
        return True


class ManejadorUnirseSala(ManejadorMensaje):
    """Maneja mensajes de tipo 'unirse_sala'"""
    
    async def manejar(self, websocket: WebSocket, data: Dict[str, Any], contexto: Dict[str, Any]) -> bool:
        tipo = data.get("tipo")
        ConsoleLogger.patron(
            "CHAIN OF RESPONSIBILITY",
            f"ManejadorUnirseSala procesando mensaje",
            f"Tipo recibido: {tipo}"
        )
        
        if tipo != "unirse_sala":
            print(f"{Fore.YELLOW}     Pasando al siguiente manejador...")
            return await self._siguiente.manejar(websocket, data, contexto) if self._siguiente else False
        
        facade = ChatFacade()
        nombre_sala = data.get("nombre_sala")
        usuario_actual = contexto.get("usuario_actual")
        sala_actual = contexto.get("sala_actual")
        
        if sala_actual:
            ConsoleLogger.websocket(
                "Saliendo de sala anterior",
                usuario=usuario_actual,
                sala=sala_actual
            )
            mensaje_salida = MensajeFactory.crear_mensaje_salida(usuario_actual)
            await broadcast_a_sala(sala_actual, mensaje_salida.to_dict())
            facade.desconectar_usuario(websocket)
        
        facade.unir_usuario_a_sala(websocket, usuario_actual, nombre_sala)
        contexto["sala_actual"] = nombre_sala
        
        usuarios_sala = facade.obtener_usuarios_de_sala(nombre_sala)
        
        await WebSocketAdapter.enviar_dict(websocket, {
            "tipo": "sala_unida",
            "sala": nombre_sala,
            "usuarios": usuarios_sala
        })
        
        mensaje_entrada = MensajeFactory.crear_mensaje_entrada(usuario_actual, usuarios_sala)
        await broadcast_a_sala(nombre_sala, mensaje_entrada.to_dict())
        
        await notificar_salas_globalmente()
        
        return True


class ManejadorMensajeChat(ManejadorMensaje):
    """Maneja mensajes de tipo 'mensaje' (chat normal)"""
    
    async def manejar(self, websocket: WebSocket, data: Dict[str, Any], contexto: Dict[str, Any]) -> bool:
        tipo = data.get("tipo")
        ConsoleLogger.patron(
            "CHAIN OF RESPONSIBILITY",
            f"ManejadorMensajeChat procesando mensaje",
            f"Tipo recibido: {tipo}"
        )
        
        if tipo != "mensaje":
            print(f"{Fore.YELLOW}     Pasando al siguiente manejador...")
            return await self._siguiente.manejar(websocket, data, contexto) if self._siguiente else False
        
        contenido = data.get("contenido")
        usuario_actual = contexto.get("usuario_actual")
        sala_actual = contexto.get("sala_actual")
        
        ConsoleLogger.mensaje("CHAT", usuario_actual, contenido, sala_actual)
        
        mensaje = MensajeFactory.crear_mensaje_chat(usuario_actual, contenido)
        await broadcast_a_sala(sala_actual, mensaje.to_dict())
        
        return True


class ManejadorObtenerSalas(ManejadorMensaje):
    """Maneja mensajes de tipo 'obtener_salas'"""
    
    async def manejar(self, websocket: WebSocket, data: Dict[str, Any], contexto: Dict[str, Any]) -> bool:
        tipo = data.get("tipo")
        ConsoleLogger.patron(
            "CHAIN OF RESPONSIBILITY",
            f"ManejadorObtenerSalas procesando mensaje",
            f"Tipo recibido: {tipo}"
        )
        
        if tipo != "obtener_salas":
            print(f"{Fore.YELLOW}     Mensaje no manejado por ningún handler")
            return False
        
        facade = ChatFacade()
        salas = facade.obtener_info_salas()
        
        await WebSocketAdapter.enviar_dict(websocket, {
            "tipo": "salas_disponibles",
            "salas": salas
        })
        
        return True


#  PATRÓN STRATEGY - Diferentes estrategias de broadcast
class EstrategiaBroadcast(ABC):
    """ STRATEGY - Interfaz para diferentes estrategias de difusión"""
    
    @abstractmethod
    async def difundir(self, mensaje: Dict[str, Any]):
        pass


class BroadcastSala(EstrategiaBroadcast):
    """Estrategia para difundir mensajes solo en una sala"""
    
    def __init__(self, nombre_sala: str):
        self.nombre_sala = nombre_sala
    
    async def difundir(self, mensaje: Dict[str, Any]):
        ConsoleLogger.patron(
            "STRATEGY",
            "Ejecutando BroadcastSala",
            f"Sala: {self.nombre_sala} | Tipo mensaje: {mensaje.get('tipo')}"
        )
        
        facade = ChatFacade()
        sala = facade.salas.get(self.nombre_sala)
        
        if sala:
            usuarios = sala.obtener_nombres_usuarios()
            print(f"{Fore.CYAN}    Difundiendo a {len(usuarios)} usuarios: {usuarios}")
            
            for ws in sala.obtener_websockets():
                try:
                    await WebSocketAdapter.enviar_dict(ws, mensaje)
                except:
                    pass


class BroadcastGlobal(EstrategiaBroadcast):
    """Estrategia para difundir mensajes a todos los usuarios conectados"""
    
    async def difundir(self, mensaje: Dict[str, Any]):
        ConsoleLogger.patron(
            "STRATEGY",
            "Ejecutando BroadcastGlobal",
            f"Tipo mensaje: {mensaje.get('tipo')}"
        )
        
        facade = ChatFacade()
        total = len(facade.conexiones)
        
        print(f"{Fore.CYAN}    Difundiendo globalmente a {total} usuarios")
        
        for websocket in list(facade.conexiones.keys()):
            try:
                await WebSocketAdapter.enviar_dict(websocket, mensaje)
            except:
                pass


# ===========================
# FUNCIONES DE UTILIDAD
# ===========================

async def broadcast_a_sala(nombre_sala: str, mensaje: Dict[str, Any]):
    """Utiliza Strategy para broadcast a una sala específica"""
    estrategia = BroadcastSala(nombre_sala)
    await estrategia.difundir(mensaje)


async def notificar_salas_globalmente():
    """Notifica a todos los usuarios sobre cambios en salas disponibles"""
    facade = ChatFacade()
    salas = facade.obtener_info_salas()
    
    estrategia = BroadcastGlobal()
    await estrategia.difundir({
        "tipo": "salas_disponibles",
        "salas": salas
    })


# ===========================
# APLICACIÓN FASTAPI
# ===========================

app = FastAPI(title="Chat Colaborativo con Patrones de Diseño")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket que usa Chain of Responsibility para manejar mensajes"""
    await websocket.accept()
    
    ConsoleLogger.websocket("WebSocket aceptado", extra="Esperando autenticación...")
    
    #  CHAIN OF RESPONSIBILITY - Construir cadena de manejadores
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print(f"{Fore.YELLOW} Construyendo Chain of Responsibility")
    print(f"{Fore.MAGENTA}{'='*80}")
    
    manejador_conectar = ManejadorConectar()
    manejador_crear = ManejadorCrearSala()
    manejador_unirse = ManejadorUnirseSala()
    manejador_mensaje = ManejadorMensajeChat()
    manejador_salas = ManejadorObtenerSalas()
    
    manejador_conectar\
        .establecer_siguiente(manejador_crear)\
        .establecer_siguiente(manejador_unirse)\
        .establecer_siguiente(manejador_mensaje)\
        .establecer_siguiente(manejador_salas)
    
    print(f"{Fore.GREEN} Cadena de responsabilidad construida\n")
    
    # Contexto compartido entre manejadores
    contexto = {
        "usuario_actual": None,
        "sala_actual": None
    }
    
    try:
        while True:
            data = await websocket.receive_json()
            
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{Fore.WHITE} MENSAJE RECIBIDO: {data}")
            print(f"{Fore.CYAN}{'='*80}\n")
            
            # Delegar al primer manejador de la cadena
            await manejador_conectar.manejar(websocket, data, contexto)
    
    except WebSocketDisconnect:
        ConsoleLogger.websocket(
            "DESCONEXIÓN DETECTADA",
            usuario=contexto.get("usuario_actual", "Desconocido"),
            sala=contexto.get("sala_actual", "Ninguna")
        )
        
        facade = ChatFacade()
        sala_actual = contexto.get("sala_actual")
        usuario_actual = contexto.get("usuario_actual")
        
        if sala_actual and usuario_actual:
            mensaje_salida = MensajeFactory.crear_mensaje_salida(usuario_actual)
            await broadcast_a_sala(sala_actual, mensaje_salida.to_dict())
        
        facade.desconectar_usuario(websocket)
        await notificar_salas_globalmente()
    
    except Exception as e:
        ConsoleLogger.error(f"Error en websocket", str(e))
        facade = ChatFacade()
        facade.desconectar_usuario(websocket)


@app.get("/")
async def get_index():
    """Sirve el archivo HTML principal"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Error: archivo index.html no encontrado</h1>", status_code=404)


@app.get("/health")
async def health_check():
    """Endpoint de salud del servidor usando Facade"""
    ConsoleLogger.patron(
        "FACADE",
        "Health check solicitado",
        "Consultando estado del sistema"
    )
    
    facade = ChatFacade()
    estado = {
        "status": "ok",
        "salas_activas": len(facade.salas),
        "usuarios_conectados": len(facade.conexiones)
    }
    
    ConsoleLogger.estado("Health Check", estado)
    
    return estado


if __name__ == "__main__":
    import uvicorn
    
    
    print(f" SERVIDOR DE CHAT CON PATRONES DE DISEÑO {Style.RESET_ALL}")
    print(f" PATRONES IMPLEMENTADOS:")
    print(f"  Creacionales:")
    print(f"      • Singleton (ChatFacade)")
    print(f"      • Factory Method (MensajeFactory)")
    print(f"      • Builder (SalaBuilder)")
    print(f"  Estructurales:")
    print(f"      • Facade (ChatFacade)")
    print(f"      • Adapter (WebSocketAdapter)")
    print(f"  Comportamiento:")
    print(f"      • Observer (SalaObservable)")
    print(f"      • Chain of Responsibility (ManejadorMensaje)")
    print(f"      • Strategy (EstrategiaBroadcast)")
 
    print(f" SERVIDOR:")
    print(f"   • URL: http://localhost:8000")
    print(f"   • WebSocket: ws://localhost:8000/ws")
    print(f"   • Health Check: http://localhost:8000/health")
    print(f" Logging detallado activado - Observa las interacciones en tiempo real!")

    
    uvicorn.run(app, host="10.253.4.194", port=8000, log_level="info")