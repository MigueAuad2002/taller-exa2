from app.repos import notificaciones_repos
from app.classes.websocket_manager import manager

async def enviar_push_nueva_emergencia(nro_emergencia: int, tipo_emergencia: str):
    roles_destino = ['ADMINISTRADOR', 'GERENTE TALLER', 'MECANICO']
    
    # 1. Buscamos a quién avisar
    usuarios_destino = notificaciones_repos.obtener_usuarios_por_roles(roles_destino)
    print(usuarios_destino)
    # 2. Armamos la notificación Push
    mensaje_push = {
        "tipo_alerta": "NUEVA_EMERGENCIA",
        "titulo": "¡Nueva Emergencia Reportada!",
        "cuerpo": f"Se requiere asistencia: {tipo_emergencia}",
        "data": {
            "nro_emergencia": nro_emergencia
        }
    }
    
    # 3. Disparamos la alerta a todos en tiempo real
    for u in usuarios_destino:
        nro_usu = u['nro_usuario']
        await manager.send_personal_message(mensaje_push, nro_usu)


#async def enviar_push_nueva_cotizacion(nro_cotizacion):