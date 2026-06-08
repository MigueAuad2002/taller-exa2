from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.classes.websocket_manager import manager
from app.utils.security import decode_access_token

# Definimos el router. Le agregamos el prefijo si gustas, pero para asegurar 
# que acepte tu URL de Postman, mapearemos la ruta exacta.
router = APIRouter(tags=["WebSockets Notificaciones"])

# Ponemos exactamente la URL que llamaste en Postman para evitar confusiones de ruteo
@router.websocket("/notificaciones")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Aceptamos el handshake inicial inmediatamente para evitar bloqueos por middleware/CORS globales
    await websocket.accept()
    
    print("\n📡 [WEBSOCKET INCOMING] Intento de conexión recibido...")
    print(f"🔑 Token enviado por URL: {token[:30]}...")

    # 1. Validar el token decodificándolo
    validation = decode_access_token(token)
    print(f"📊 Resultado del decode: {validation}")
    
    # Comprobación flexible del resultado de tu función de seguridad
    if not validation or (isinstance(validation, dict) and validation.get('success') is False):
        print("❌ CONEXIÓN RECHAZADA: El token es inválido o expiró.")
        await websocket.close(code=1008)
        return

    # 2. Extraer el payload de forma segura según la estructura de tu JWT
    payload = validation.get('payload') if isinstance(validation, dict) else None
    if not payload:
        # Si los datos vienen directo o bajo la llave 'data'
        payload = validation.get('data', validation) if isinstance(validation, dict) else validation

    try:
        nro_usuario = payload.get('nro_usuario')
    except Exception:
        nro_usuario = None

    if not nro_usuario:
        print("❌ CONEXIÓN RECHAZADA: No se encontró 'nro_usuario' en el payload del Token.")
        await websocket.close(code=1008)
        return

    print(f"👤 Token válido. Vinculando canal al nro_usuario: {nro_usuario}")

    # 3. Guardar la conexión activa en nuestro manager para retransmitir
    manager.active_connections[int(nro_usuario)] = websocket
    print(f"🟢 Canal en tiempo real abierto exitosamente para el usuario {nro_usuario}.")
    
    try:
        while True:
            # Mantiene el hilo escuchando peticiones o pings para que no se cierre
            await websocket.receive_text()
    except WebSocketDisconnect:
        if int(nro_usuario) in manager.active_connections:
            del manager.active_connections[int(nro_usuario)]
        print(f"🔴 Usuario {nro_usuario} desconectado del WebSocket.")