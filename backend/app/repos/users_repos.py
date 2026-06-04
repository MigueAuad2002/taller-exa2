from app.classes.postgres import PostgreSQL
from app.config import Config

# --- LEER USUARIOS ---
def obtener_todos_los_usuarios():
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"""
            SELECT 
                a.nro_usuario, a.ci, a.nombre_usuario, a.estado, a.id_empresa,
                b.nombre_completo, b.correo, b.telefono, b.direccion,
                c.nombre_rol, a.nro_rol
            FROM {Config.SCHEMA}.usuario a
            INNER JOIN {Config.SCHEMA}.persona b ON a.ci = b.ci
            INNER JOIN {Config.SCHEMA}.rol c ON a.nro_rol = c.nro_rol
            WHERE a.estado = 'ACTIVO';
        """
        resultados = db.execute_query(query, fetchall=True)
        
        usuarios = []
        if resultados:
            for r in resultados:
                usuarios.append({
                    "nro_usuario": r[0], "ci": r[1], "nombre_usuario": r[2], 
                    "estado": r[3], "id_empresa": r[4], "nombre_completo": r[5], 
                    "correo": r[6], "telefono": r[7], "direccion": r[8], 
                    "nombre_rol": r[9], "nro_rol": r[10] # nro_rol añadido para el frontend
                })
        return usuarios
    finally:
        db.close_connection()

# --- CREAR USUARIO (Opción A) ---
def crear_usuario_db(datos_persona, datos_usuario):
    db = PostgreSQL()
    db.create_connection()
    try:
        # 1. Primero verificamos si el usuario ya existe para cortar el flujo de inmediato
        # datos_usuario[3] corresponde al 'ci' y datos_usuario[0] al 'nombre_usuario'
        query_verificar = f"""
            SELECT nro_usuario FROM {Config.SCHEMA}.usuario 
            WHERE ci = %s OR nombre_usuario = %s AND estado = 'ACTIVO';
        """
        existe = db.execute_query(query_verificar, (datos_usuario[3], datos_usuario[0]), fetchone=True)
        if existe:
            print("ERROR: El CI o el Nombre de Usuario ya se encuentran registrados.")
            return None # Aquí sí cortará y devolverá None a tu servicio

        # 2. Insertar Persona (Quitamos ON CONFLICT para mantener la integridad real)
        query_persona = f"""
            INSERT INTO {Config.SCHEMA}.persona (ci, nombre_completo, telefono, correo, direccion)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (ci) DO UPDATE 
            SET nombre_completo = EXCLUDED.nombre_completo,
                telefono = EXCLUDED.telefono,
                correo = EXCLUDED.correo,
                direccion = EXCLUDED.direccion;
        """
        db.execute_query(query_persona, datos_persona)

        # 3. Insertar Usuario
        query_usuario = f"""
            INSERT INTO {Config.SCHEMA}.usuario (nombre_usuario, password_hash, estado, ci, nro_rol, id_empresa)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING nro_usuario;
        """
        resultado = db.execute_query(query_usuario, datos_usuario, fetchone=True, commit=True)
        
        return resultado[0] if resultado else None
    finally:
        db.close_connection()

# --- ACTUALIZAR USUARIO ---
def actualizar_usuario_db(nro_usuario, ci, datos_persona, datos_usuario, cambiar_password=False):
    db = PostgreSQL()
    db.create_connection()
    try:
        # 1. Actualizar Persona 
        query_persona = f"""
            UPDATE {Config.SCHEMA}.persona
            SET nombre_completo = %s, telefono = %s, correo = %s, direccion = %s
            WHERE ci = %s;
        """
        db.execute_query(query_persona, datos_persona + (ci,))

        # 2. Actualizar Usuario 
        if cambiar_password:
            query_usuario = f"""
                UPDATE {Config.SCHEMA}.usuario
                SET nombre_usuario = %s, password_hash = %s, nro_rol = %s, id_empresa = %s
                WHERE nro_usuario = %s;
            """
        else:
            query_usuario = f"""
                UPDATE {Config.SCHEMA}.usuario
                SET nombre_usuario = %s, nro_rol = %s, id_empresa = %s
                WHERE nro_usuario = %s;
            """
        
        db.execute_query(query_usuario, datos_usuario + (nro_usuario,), commit=True)
        return True
    finally:
        db.close_connection()

# --- ELIMINAR USUARIO (Baja Lógica) ---
def eliminar_usuario_db(nro_usuario: int):
    db = PostgreSQL()
    db.create_connection()
    try:
        query = f"UPDATE {Config.SCHEMA}.usuario SET estado = 'INACTIVO' WHERE nro_usuario = %s;"
        db.execute_query(query, (nro_usuario,), commit=True)
        return True
    finally:
        db.close_connection()