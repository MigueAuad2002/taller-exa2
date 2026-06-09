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
from app.repos import notificaciones_repos
from app.classes.websocket_manager import manager

async def enviar_push_nueva_emergencia(nro_emergencia: int, tipo_emergencia: str):
    # Definimos los roles que deben enterarse del evento (de Cliente a Taller/Admin)
    roles_destino = ['ADMINISTRADOR', 'GERENTE TALLER', 'MECANICO']
    
    # 1. Buscamos a qué usuarios activos avisar según su rol
    usuarios_destino = notificaciones_repos.obtener_usuarios_por_roles(roles_destino)
    print(f"📡 Usuarios destino encontrados en BD: {usuarios_destino}")
    
    # 2. Armamos el esqueleto de la notificación
    titulo_alerta = "¡Nueva Emergencia Reportada!"
    cuerpo_alerta = f"Se requiere asistencia: {tipo_emergencia}"
    
    mensaje_push = {
        "tipo_alerta": "NUEVA_EMERGENCIA",
        "titulo": titulo_alerta,
        "cuerpo": cuerpo_alerta,
        "data": {
            "nro_emergencia": nro_emergencia
        }
    }
    
    # 3. Guardamos en la Base de Datos y disparamos en tiempo real
    for u in usuarios_destino:
        nro_usu = u['nro_usuario']
        
        # A) GUARDAR EN LA BD (Persistencia obligatoria para la materia)
        try:
            notificaciones_repos.guardar_notificacion_db(
                titulo=titulo_alerta,
                cuerpo=cuerpo_alerta,
                tipo_referencia="NUEVA_EMERGENCIA",
                nro_usuario=int(nro_usu),
                nro_emergencia=int(nro_emergencia)
            )
            print(f"💾 Notificación guardada en BD para el usuario {nro_usu}")
        except Exception as db_err:
            print(f"⚠️ Error al guardar notificación para el usuario {nro_usu}: {str(db_err)}")
        
        # B) TRANSMITIR POR WEBSOCKET (Tiempo real)
        await manager.send_personal_message(mensaje_push, nro_usu)
async def enviar_notificacion_a_cliente(nro_usuario_cliente: int, nro_emergencia: int, mensaje_texto: str):
    titulo_alerta = "¡Tu emergencia tiene una nueva oferta!"
    
    mensaje_push = {
        "tipo_alerta": "NUEVA_OFERTA",
        "titulo": titulo_alerta,
        "cuerpo": mensaje_texto,
        "data": {"nro_emergencia": nro_emergencia}
    }
    
    # 1. Guardar en la BD para el cliente
    notificaciones_repos.guardar_notificacion_db(
        titulo=titulo_alerta,
        cuerpo=mensaje_texto,
        tipo_referencia="NUEVA_OFERTA",
        nro_usuario=nro_usuario_cliente,
        nro_emergencia=nro_emergencia
    )
    
    # 2. Enviar en vivo si el cliente está conectado en su app móvil
    await manager.send_personal_message(mensaje_push, nro_usuario_cliente)
def listar_mis_notificaciones(nro_usuario: int):
    if not nro_usuario:
        raise ValueError("No se pudo identificar al usuario de la sesión.")
    
    alertas = notificaciones_repos.obtener_notificaciones_por_usuario_db(int(nro_usuario))
    return {
        "success": True,
        "message": "Bandeja de notificaciones recuperada exitosamente.",
        "data": alertas
    }

def cambiar_estado_leido(nro_usuario: int, id_notificacion: int = None, marcar_todo: bool = False):
    if not nro_usuario:
        raise ValueError("Operación no autorizada. Sesión inválida.")
        
    # ESCENARIO A: Botón masivo para limpiar toda la bandeja
    if marcar_todo:
        total_actualizadas = notificaciones_repos.marcar_todas_las_notificaciones_leidas_db(int(nro_usuario))
        return {
            "success": True,
            "message": f"Todas las notificaciones fueron marcadas como leídas. ({total_actualizadas} alertas afectadas)"
        }
        
    # ESCENARIO B: Se leyó una notificación específica
    if id_notificacion:
        exito = notificaciones_repos.marcar_notificacion_leida_db(int(id_notificacion), int(nro_usuario))
        if not exito:
            raise ValueError("No se encontró la notificación seleccionada o no te pertenece.")
        return {
            "success": True,
            "message": "Notificación marcada como leída exitosamente."
        }
        
    raise ValueError("Parámetros insuficientes para procesar la lectura de alertas.")