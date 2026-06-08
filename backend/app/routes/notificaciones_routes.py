from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.classes.websocket_manager import manager
from app.utils.security import decode_access_token


router = APIRouter(tags=["WebSockets Notificaciones"])


@router.websocket("/notificaciones")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    await websocket.accept()
    
    print("INTENTANDO CONECTAR WEBSOCKET")
    print(f"TOKEN RECIBIDO POR URL: {token[:30]}...")

    #VALIDAR EL TOKEN
    validation = decode_access_token(token)
    
    #COMPROBACION DE TOKEN
    if not validation or (isinstance(validation, dict) and validation.get('success') is False):
        print("❌ CONEXIÓN RECHAZADA: El token es inválido o expiró.")
        await websocket.close(code=1008)
        return

    #EXTRAER CONTENIDO DEL TOKEN
    payload = validation.get('payload') if isinstance(validation, dict) else None
    if not payload:
        payload = validation.get('data', validation) if isinstance(validation, dict) else validation

    try:
        nro_usuario = payload.get('nro_usuario')
    except Exception:
        nro_usuario = None

    if not nro_usuario:
        print("CONEXIÓN RECHAZADA: NO SE ENCONTRO UN NRO_USUARIO DENTRO DEL TOKEN.")
        await websocket.close(code=1008)
        return

    print(f"TOKEN VALIDO. VINCULANDO CANAL AL USUARIO: {nro_usuario}")

    #GUARDAR CONEXION ACTIVA
    manager.active_connections[int(nro_usuario)] = websocket
    print(f"CANAL EN TIEMPO REAL ABIERTO EXITOSAMENTE PARA EL USUARIO {nro_usuario}.")
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if int(nro_usuario) in manager.active_connections:
            del manager.active_connections[int(nro_usuario)]
        print(f"USUARIO {nro_usuario} DESCONECTADO DEL WEBSOCKET.")