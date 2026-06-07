from app.classes.postgres import PostgreSQL
from app.config import Config


# --- LEER TODAS LAS EMERGENCIAS (Para Administrador) ---
def obtener_todas_las_emergencias():
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT nro_emergencia, tipo_emergencia, latitud, longitud, 
                   fecha_inicio, fecha_fin, estado, prioridad, 
                   nro_usuario, nro_taller, id_empresa
            FROM {Config.SCHEMA}.emergencia
            ORDER BY fecha_inicio DESC;
        """
        resultados = db.execute_query(query, fetchall=True)

        emergencias = []
        if resultados:
            for r in resultados:
                emergencias.append({
                    "nro_emergencia": r[0],
                    "tipo_emergencia": r[1],
                    "latitud": float(r[2]) if r[2] is not None else None,
                    "longitud": float(r[3]) if r[3] is not None else None,
                    "fecha_inicio": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None,
                    "fecha_fin": r[5].strftime("%Y-%m-%d %H:%M:%S") if r[5] else None,
                    "estado": r[6],
                    "prioridad": r[7],
                    "nro_usuario": r[8],
                    "nro_taller": r[9],
                    "id_empresa": r[10]
                })
        return emergencias
    finally:
        db.close_connection()


# --- LEER EMERGENCIAS POR USUARIO (Para el Cliente) ---
def obtener_emergencias_por_usuario(nro_usuario: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT nro_emergencia, tipo_emergencia, latitud, longitud, 
                   fecha_inicio, fecha_fin, estado, prioridad, 
                   nro_taller, id_empresa
            FROM {Config.SCHEMA}.emergencia
            WHERE nro_usuario = %s
            ORDER BY fecha_inicio DESC;
        """
        resultados = db.execute_query(query, (nro_usuario,), fetchall=True)

        emergencias = []
        if resultados:
            for r in resultados:
                emergencias.append({
                    "nro_emergencia": r[0],
                    "tipo_emergencia": r[1],
                    "latitud": float(r[2]) if r[2] is not None else None,
                    "longitud": float(r[3]) if r[3] is not None else None,
                    "fecha_inicio": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None,
                    "fecha_fin": r[5].strftime("%Y-%m-%d %H:%M:%S") if r[5] else None,
                    "estado": r[6],
                    "prioridad": r[7],
                    "nro_usuario": nro_usuario,
                    "nro_taller": r[8],
                    "id_empresa": r[9]
                })
        return emergencias
    finally:
        db.close_connection()


# --- LEER EMERGENCIAS DEL TALLER DEL MECÁNICO ---
def obtener_emergencias_por_taller_del_mecanico(nro_usuario: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT 
                e.nro_emergencia,
                e.tipo_emergencia,
                e.latitud,
                e.longitud,
                e.fecha_inicio,
                e.fecha_fin,
                e.estado,
                e.prioridad,
                e.nro_usuario,
                e.nro_taller,
                e.id_empresa,
                t.nombre_taller,
                p.nombre_completo,
                p.telefono
            FROM {Config.SCHEMA}.usuario um
            INNER JOIN {Config.SCHEMA}.taller t
                ON um.nro_taller = t.nro_taller
            INNER JOIN {Config.SCHEMA}.emergencia e
                ON e.nro_taller = t.nro_taller
            INNER JOIN {Config.SCHEMA}.usuario uc
                ON e.nro_usuario = uc.nro_usuario
            INNER JOIN {Config.SCHEMA}.persona p
                ON uc.ci = p.ci
            WHERE um.nro_usuario = %s
              AND um.nro_taller IS NOT NULL
              AND um.id_empresa IS NOT NULL
              AND t.id_empresa = um.id_empresa
            ORDER BY e.fecha_inicio DESC;
        """

        resultados = db.execute_query(query, (nro_usuario,), fetchall=True)

        emergencias = []
        if resultados:
            for r in resultados:
                emergencias.append({
                    "nro_emergencia": r[0],
                    "tipo_emergencia": r[1],
                    "latitud": float(r[2]) if r[2] is not None else None,
                    "longitud": float(r[3]) if r[3] is not None else None,
                    "fecha_inicio": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None,
                    "fecha_fin": r[5].strftime("%Y-%m-%d %H:%M:%S") if r[5] else None,
                    "estado": r[6],
                    "prioridad": r[7],
                    "nro_usuario": r[8],
                    "nro_taller": r[9],
                    "id_empresa": r[10],
                    "nombre_taller": r[11],
                    "cliente": r[12],
                    "telefono_cliente": r[13]
                })

        return emergencias
    finally:
        db.close_connection()


# --- CREAR EMERGENCIA ---
def crear_emergencia_db(tipo_emergencia, latitud, longitud, estado, prioridad, nro_usuario):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            INSERT INTO {Config.SCHEMA}.emergencia 
            (tipo_emergencia, latitud, longitud, fecha_inicio, estado, prioridad, nro_usuario) 
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s) 
            RETURNING nro_emergencia;
        """
        resultado = db.execute_query(
            query,
            (tipo_emergencia, latitud, longitud, estado, prioridad, nro_usuario),
            fetchone=True,
            commit=True
        )
        return resultado[0] if resultado else None
    finally:
        db.close_connection()


# --- ACTUALIZAR EMERGENCIA ---
def actualizar_emergencia_db(nro_emergencia, tipo_emergencia, latitud, longitud, estado, prioridad, nro_taller, id_empresa):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            UPDATE {Config.SCHEMA}.emergencia 
            SET tipo_emergencia = %s, latitud = %s, longitud = %s, 
                estado = %s, prioridad = %s, nro_taller = %s, id_empresa = %s
            WHERE nro_emergencia = %s;
        """
        filas_afectadas = db.execute_query(
            query,
            (tipo_emergencia, latitud, longitud, estado, prioridad, nro_taller, id_empresa, nro_emergencia),
            commit=True
        )
        return filas_afectadas > 0
    finally:
        db.close_connection()


# --- ELIMINAR EMERGENCIA (Borrado físico) ---
def eliminar_emergencia_db(nro_emergencia: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"DELETE FROM {Config.SCHEMA}.emergencia WHERE nro_emergencia = %s;"
        filas_afectadas = db.execute_query(query, (nro_emergencia,), commit=True)
        return filas_afectadas > 0
    finally:
        db.close_connection()