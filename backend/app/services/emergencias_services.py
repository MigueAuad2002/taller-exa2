from fastapi import BackgroundTasks
from app.repos import emergencias_repos
from app.services import notificaciones_services

#FUNCIONES DE LECTURA (GET)

def listar_todas_las_emergencias():
    emergencias = emergencias_repos.obtener_todas_las_emergencias()
    return {"success": True, "message": "Emergencias recuperadas exitosamente", "data": emergencias}

def listar_mis_emergencias(nro_usuario: int):
    emergencias = emergencias_repos.obtener_emergencias_por_usuario(nro_usuario)
    return {"success": True, "message": f"Emergencias del usuario {nro_usuario} recuperadas exitosamente", "data": emergencias}

def listar_emergencias_mi_taller(nro_usuario: int):
    if not nro_usuario:
        raise ValueError("No se pudo identificar al usuario autenticado.")
    emergencias = emergencias_repos.obtener_emergencias_por_taller_del_mecanico(nro_usuario)
    return {"success": True, "message": "Emergencias del taller del mecánico recuperadas exitosamente", "data": emergencias}

#FUNCIONES DE ESCRITURA CON NOTIFICACIONES

def normalizar_rol(rol_usuario: str):
    return rol_usuario.strip().upper() if rol_usuario else ""

def registrar_emergencia(data: dict, token_data: dict, background_tasks: BackgroundTasks):
    rol = normalizar_rol(token_data.get('nombre_rol'))
    tipo_emergencia = data.get('tipo_emergencia')
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    prioridad = data.get('prioridad', 'MEDIA')
    
    #VALIDACIONES POR ROL
    if rol == 'ADMINISTRADOR':
        nro_usuario = data.get('nro_usuario')
        if not nro_usuario:
            raise ValueError("Como Administrador, debe especificar el 'nro_usuario' para asignar la emergencia.")
    elif rol == 'CLIENTE':
        nro_usuario = token_data.get('nro_usuario')
        evidencias = data.get('evidencias', [])
        if not evidencias:
            raise ValueError("Como Cliente, es obligatorio adjuntar al menos una evidencia.")
    else:
        raise ValueError("Rol no autorizado para crear emergencias.")

    nuevo_id = emergencias_repos.crear_emergencia_db(
        tipo_emergencia.upper(), latitud, longitud, 'PENDIENTE', prioridad.upper(), nro_usuario
    )

    #PROCESAR EVIDENCIAS BASE64 AL CREAR
    if rol == 'CLIENTE' and data.get('evidencias'):
        for ev in data.get('evidencias'):
            tipo = ev.get('tipo_archivo', 'IMAGEN')
            base64_string = ev.get('base64', '')
            if base64_string:
                emergencias_repos.agregar_evidencia_db(nuevo_id, tipo.upper(), base64_string)

    #DISPARAR NOTIFICACION EN SEGUNDO PLANO
    background_tasks.add_task(
        notificaciones_services.enviar_push_nueva_emergencia, 
        nuevo_id, 
        tipo_emergencia.upper()
    )

    return {"success": True, "message": "Emergencia creada y notificaciones enviadas.", "nro_emergencia": nuevo_id}

def actualizar_emergencia(nro_emergencia: int, data: dict, token_data: dict):
    rol = normalizar_rol(token_data.get('nombre_rol'))
    nro_taller_token = token_data.get('nro_taller')

    emergencia = emergencias_repos.obtener_emergencia_por_id(nro_emergencia)
    if not emergencia:
        raise ValueError("La emergencia no existe.")

    if rol == 'ADMINISTRADOR':
        estado = data.get('estado')
        if not estado: raise ValueError("Admin solo puede actualizar el 'estado'.")
        emergencias_repos.actualizar_estado_emergencia_db(nro_emergencia, estado.upper())
    
    elif rol in ['MECANICO', 'MECÁNICO', 'TECNICO', 'TÉCNICO']:
        if emergencia['nro_taller'] != nro_taller_token:
            raise ValueError("Acceso Denegado: Emergencia no asignada a tu taller.")
        estado = data.get('estado')
        if not estado: raise ValueError("Mecánico solo puede actualizar el 'estado'.")
        emergencias_repos.actualizar_estado_emergencia_db(nro_emergencia, estado.upper())
    
    #PROCESAR EVIDENCIAS BASE64 AL ACTUALIZAR
    elif rol == 'CLIENTE':
        if emergencia['nro_usuario'] != token_data.get('nro_usuario'):
            raise ValueError("No puedes modificar emergencias de otros.")
            
        añadir = data.get('añadir_evidencias', [])
        eliminar = data.get('eliminar_evidencias', [])
        
        for ev in añadir: 
            tipo = ev.get('tipo_archivo', 'IMAGEN')
            base64_string = ev.get('base64', '')
            if base64_string:
                emergencias_repos.agregar_evidencia_db(nro_emergencia, tipo.upper(), base64_string)
                
        for id_ev in eliminar: 
            emergencias_repos.eliminar_evidencia_db(id_ev)
    
    return {"success": True, "message": "Emergencia actualizada correctamente."}

def borrar_emergencia(nro_emergencia: int, token_data: dict):
    rol = normalizar_rol(token_data.get('nombre_rol'))
    emergencia = emergencias_repos.obtener_emergencia_por_id(nro_emergencia)
    if not emergencia: raise ValueError("Emergencia no encontrada.")
    if rol == 'CLIENTE' and emergencia['nro_usuario'] != token_data.get('nro_usuario'):
        raise ValueError("No tienes permiso para borrar esto.")
    
    emergencias_repos.eliminar_emergencia_db(nro_emergencia)
    return {"success": True, "message": "Emergencia eliminada."}