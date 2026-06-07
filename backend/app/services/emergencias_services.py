from app.repos import emergencias_repos


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


def registrar_emergencia(data: dict):
    tipo_emergencia = data.get('tipo_emergencia')
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    prioridad = data.get('prioridad', 'MEDIA')
    nro_usuario = data.get('nro_usuario')

    estado_inicial = 'PENDIENTE'

    if not tipo_emergencia or not nro_usuario:
        raise ValueError("Los campos 'tipo_emergencia' y 'nro_usuario' son obligatorios.")

    nuevo_id = emergencias_repos.crear_emergencia_db(
        tipo_emergencia.upper(),
        latitud,
        longitud,
        estado_inicial,
        prioridad.upper(),
        nro_usuario
    )

    return {
        "success": True,
        "message": "Emergencia reportada exitosamente",
        "nro_emergencia": nuevo_id
    }


def actualizar_emergencia(nro_emergencia: int, data: dict):
    if nro_emergencia <= 0:
        raise ValueError("ID de emergencia no válido.")

    tipo_emergencia = data.get('tipo_emergencia')
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    estado = data.get('estado')
    prioridad = data.get('prioridad')
    nro_taller = data.get('nro_taller')
    id_empresa = data.get('id_empresa')

    if not tipo_emergencia or not estado:
        raise ValueError("Los campos 'tipo_emergencia' y 'estado' son obligatorios para actualizar.")

    exito = emergencias_repos.actualizar_emergencia_db(
        nro_emergencia,
        tipo_emergencia.upper(),
        latitud,
        longitud,
        estado.upper(),
        prioridad.upper() if prioridad else None,
        nro_taller,
        id_empresa
    )

    if not exito:
        raise ValueError(f"No se pudo actualizar. La emergencia con ID {nro_emergencia} no existe.")

    return {
        "success": True,
        "message": "Emergencia actualizada exitosamente"
    }


def borrar_emergencia(nro_emergencia: int):
    if nro_emergencia <= 0:
        raise ValueError("ID de emergencia no válido.")

    exito = emergencias_repos.eliminar_emergencia_db(nro_emergencia)

    if not exito:
        raise ValueError(f"No se pudo eliminar. La emergencia con ID {nro_emergencia} no existe.")

    return {
        "success": True,
        "message": "Emergencia eliminada permanentemente de la base de datos."
    }