from app.repos import emergencias_repos

# --- FUNCIONES DE LECTURA (GET) QUE YA TENÍAS ---

def listar_todas_las_emergencias():
    emergencias = emergencias_repos.obtener_todas_las_emergencias()
    return {
        "success": True,
        "message": "Emergencias recuperadas exitosamente",
        "data": emergencias
    }

def listar_mis_emergencias(nro_usuario: int):
    emergencias = emergencias_repos.obtener_emergencias_por_usuario(nro_usuario)
    return {
        "success": True,
        "message": f"Emergencias del usuario {nro_usuario} recuperadas exitosamente",
        "data": emergencias
    }

def listar_emergencias_mi_taller(nro_usuario: int):
    if not nro_usuario:
        raise ValueError("No se pudo identificar al usuario autenticado.")
    emergencias = emergencias_repos.obtener_emergencias_por_taller_del_mecanico(nro_usuario)
    return {
        "success": True,
        "message": "Emergencias del taller del mecánico recuperadas exitosamente",
        "data": emergencias
    }

# --- NUEVAS FUNCIONES DE ESCRITURA (POST, PUT, DELETE) CON REGLAS DE ROLES ---

def normalizar_rol(rol_usuario: str):
    return rol_usuario.strip().upper() if rol_usuario else ""

def registrar_emergencia(data: dict, token_data: dict):
    rol = normalizar_rol(token_data.get('nombre_rol'))
    tipo_emergencia = data.get('tipo_emergencia')
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    prioridad = data.get('prioridad', 'MEDIA')
    
    # 1. VALIDACIÓN DEL ADMIN
    if rol == 'ADMINISTRADOR':
        nro_usuario = data.get('nro_usuario')
        if not nro_usuario:
            raise ValueError("Como Administrador, debe especificar el 'nro_usuario' para asignar la emergencia al cliente.")
    
    # 2. VALIDACIÓN DEL CLIENTE (Evidencias Obligatorias)
    elif rol == 'CLIENTE':
        nro_usuario = token_data.get('nro_usuario') # Autogestión
        evidencias = data.get('evidencias') # Esperamos una lista de URLs/Archivos
        if not evidencias or len(evidencias) == 0:
            raise ValueError("Como Cliente, es obligatorio adjuntar al menos una evidencia (foto/audio) al reportar la emergencia.")

    estado_inicial = 'PENDIENTE'

    # Crear la emergencia base
    nuevo_id = emergencias_repos.crear_emergencia_db(
        tipo_emergencia.upper(), latitud, longitud, estado_inicial, prioridad.upper(), nro_usuario
    )

    # Si es cliente, insertar automáticamente las evidencias en la BD
    if rol == 'CLIENTE' and data.get('evidencias'):
        for url in data.get('evidencias'):
            emergencias_repos.agregar_evidencia_db(nuevo_id, url)

    return {
        "success": True,
        "message": "Emergencia reportada exitosamente con sus evidencias",
        "nro_emergencia": nuevo_id
    }

def actualizar_emergencia(nro_emergencia: int, data: dict, token_data: dict):
    rol = normalizar_rol(token_data.get('nombre_rol'))
    nro_usuario_token = token_data.get('nro_usuario')
    nro_taller_token = token_data.get('nro_taller')

    emergencia = emergencias_repos.obtener_emergencia_por_id(nro_emergencia)
    if not emergencia:
        raise ValueError("La emergencia solicitada no existe.")

    # 1. REGLA DEL ADMINISTRADOR (Solo modifica estado)
    if rol == 'ADMINISTRADOR':
        estado = data.get('estado')
        if not estado:
            raise ValueError("Como Administrador, el único campo que puedes actualizar es el 'estado'.")
        emergencias_repos.actualizar_estado_emergencia_db(nro_emergencia, estado.upper())

    # 2. REGLA DEL MECÁNICO (Solo modifica estado Y debe ser de su taller)
    elif rol in ['MECANICO', 'MECÁNICO', 'TECNICO', 'TÉCNICO']:
        if emergencia['nro_taller'] != nro_taller_token:
            raise ValueError("Acceso Denegado. Esta emergencia no está asignada a tu taller.")
        
        estado = data.get('estado')
        if not estado:
            raise ValueError("Como Mecánico, el único campo que puedes actualizar es el 'estado'.")
        emergencias_repos.actualizar_estado_emergencia_db(nro_emergencia, estado.upper())

    # 3. REGLA DEL CLIENTE (Solo modifica evidencias Y debe ser suyo)
    elif rol == 'CLIENTE':
        if emergencia['nro_usuario'] != nro_usuario_token:
            raise ValueError("Acceso Denegado. No puedes modificar una emergencia que no te pertenece.")
        
        añadir = data.get('añadir_evidencias', [])
        eliminar = data.get('eliminar_evidencias', []) # Espera una lista de IDs de evidencia

        if not añadir and not eliminar:
            raise ValueError("Como Cliente, la acción de actualizar solo permite 'añadir_evidencias' o 'eliminar_evidencias'.")

        for url in añadir:
            emergencias_repos.agregar_evidencia_db(nro_emergencia, url)
        for id_evidencia in eliminar:
            emergencias_repos.eliminar_evidencia_db(id_evidencia)

    return {"success": True, "message": "Emergencia actualizada correctamente según tu rol."}

def borrar_emergencia(nro_emergencia: int, token_data: dict):
    rol = normalizar_rol(token_data.get('nombre_rol'))
    
    emergencia = emergencias_repos.obtener_emergencia_por_id(nro_emergencia)
    if not emergencia:
        raise ValueError("La emergencia solicitada no existe.")

    # REGLA DEL CLIENTE: Solo borra las suyas
    if rol == 'CLIENTE' and emergencia['nro_usuario'] != token_data.get('nro_usuario'):
        raise ValueError("Acceso Denegado. No puedes eliminar emergencias de otros usuarios.")

    # Si es Admin pasa directo. (El mecánico es bloqueado desde las Rutas).
    emergencias_repos.eliminar_emergencia_db(nro_emergencia)
    
    return {"success": True, "message": "Emergencia eliminada permanentemente de la base de datos."}