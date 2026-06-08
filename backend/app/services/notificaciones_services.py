from app.repos import notificaciones_repos
from app.classes.websocket_manager import manager

#ALERTA A TODOS LOS TALLERES (CUANDO SE CREA LA EMERGENCIA)
async def enviar_push_nueva_emergencia(nro_emergencia: int, tipo_emergencia: str):
    roles_destino = ['ADMINISTRADOR', 'GERENTE TALLER', 'MECANICO']
    usuarios_destino = notificaciones_repos.obtener_usuarios_por_roles(roles_destino)
    
    titulo = "¡Nueva Emergencia Reportada!"
    cuerpo = f"Se requiere asistencia: {tipo_emergencia}"
    tipo_ref = "NUEVA_EMERGENCIA"

    mensaje_push = {
        "tipo_alerta": tipo_ref,
        "titulo": titulo,
        "cuerpo": cuerpo,
        "data": {"nro_emergencia": nro_emergencia}
    }
    
    for u in usuarios_destino:
        nro_usu = u['nro_usuario']
        # 1. Guardar en base de datos
        notificaciones_repos.guardar_notificacion_db(titulo, cuerpo, tipo_ref, nro_usu, nro_emergencia)
        # 2. Enviar por WebSocket
        await manager.send_personal_message(mensaje_push, nro_usu)

#ALERTA AL CLIENTE (CUANDO UN TALLER LE MANDA UNA OFERTA)
async def enviar_push_nueva_oferta(nro_emergencia: int, id_oferta: int, nro_usuario_cliente: int, precio: float):
    titulo = "¡Nueva Oferta Recibida!"
    cuerpo = f"Un taller ha ofrecido atender su emergencia por Bs. {precio}."
    tipo_ref = "NUEVA_OFERTA"

    # 1. Guardar en base de datos
    notificaciones_repos.guardar_notificacion_db(titulo, cuerpo, tipo_ref, nro_usuario_cliente, nro_emergencia)

    # 2. Enviar por WebSocket
    mensaje_push = {
        "tipo_alerta": tipo_ref,
        "titulo": titulo,
        "cuerpo": cuerpo,
        "data": {"nro_emergencia": nro_emergencia, "id_oferta": id_oferta}
    }
    await manager.send_personal_message(mensaje_push, nro_usuario_cliente)

#ALERTA A LOS TRABAJADORES DEL TALLER (CUANDO EL CLIENTE RESPONDE LA OFERTA)
async def enviar_push_respuesta_oferta(nro_emergencia: int, id_oferta: int, estado_respuesta: str, nro_taller: int):
    usuarios_taller = notificaciones_repos.obtener_usuarios_por_taller(nro_taller)
    
    if estado_respuesta == 'ACEPTADA':
        titulo = "¡Oferta Aceptada!"
        cuerpo = "El cliente aceptó tu cotización. ¡Inicia el trayecto!"
    else:
        titulo = "Oferta Rechazada"
        cuerpo = "El cliente ha declinado tu cotización."
        
    tipo_ref = "RESPUESTA_OFERTA"

    mensaje_push = {
        "tipo_alerta": tipo_ref,
        "titulo": titulo,
        "cuerpo": cuerpo,
        "data": {"nro_emergencia": nro_emergencia, "id_oferta": id_oferta}
    }
    
    for u in usuarios_taller:
        nro_usu = u['nro_usuario']
        # 1. Guardar en BD para cada miembro del taller
        notificaciones_repos.guardar_notificacion_db(titulo, cuerpo, tipo_ref, nro_usu, nro_emergencia)
        # 2. Notificar por WebSocket
        await manager.send_personal_message(mensaje_push, nro_usu)