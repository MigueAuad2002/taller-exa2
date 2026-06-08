from app.classes.postgres import PostgreSQL
from app.config import Config

#OBTENER USUARIOS POR ROL (PARA NUEVA EMERGENCIA)
def obtener_usuarios_por_roles(roles: list):
    db = PostgreSQL()
    db.create_connection()
    try:
        format_strings = ','.join(['%s'] * len(roles))
        query = f"""
            SELECT u.nro_usuario, u.nombre_usuario, r.nombre_rol
            FROM {Config.SCHEMA}.usuario u
            INNER JOIN {Config.SCHEMA}.rol r ON u.nro_rol = r.nro_rol
            WHERE UPPER(r.nombre_rol) IN ({format_strings}) AND u.estado = 'ACTIVO';
        """
        roles_upper = [rol.upper() for rol in roles]
        resultados = db.execute_query(query, tuple(roles_upper), fetchall=True)
        
        usuarios = []
        if resultados:
            for r in resultados:
                usuarios.append({
                    "nro_usuario": r[0],
                    "nombre_usuario": r[1],
                    "nombre_rol": r[2]
                })
        return usuarios
    finally:
        db.close_connection()

#OBTENER USUARIOS DE UN TALLER ESPECÍFICO (CUANDO EL CLIENTE ACEPTA/RECHAZA)
def obtener_usuarios_por_taller(nro_taller: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT nro_usuario, nombre_usuario 
            FROM {Config.SCHEMA}.usuario 
            WHERE nro_taller = %s AND estado = 'ACTIVO';
        """
        resultados = db.execute_query(query, (nro_taller,), fetchall=True)
        
        usuarios = []
        if resultados:
            for r in resultados:
                usuarios.append({
                    "nro_usuario": r[0],
                    "nombre_usuario": r[1]
                })
        return usuarios
    finally:
        db.close_connection()

#GUARDAR NOTIFICACIÓN EN LA BASE DE DATOS
def guardar_notificacion_db(titulo: str, cuerpo: str, tipo_referencia: str, nro_usuario: int, nro_emergencia: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            INSERT INTO {Config.SCHEMA}.notificacion 
            (titulo, cuerpo, tipo_referencia, nro_usuario, nro_emergencia) 
            VALUES (%s, %s, %s, %s, %s);
        """
        db.execute_query(query, (titulo, cuerpo, tipo_referencia, nro_usuario, nro_emergencia), commit=True)
    finally:
        db.close_connection()