from app.classes.postgres import PostgreSQL
from app.config import Config

def obtener_usuarios_por_roles(roles: list):
    db = PostgreSQL()
    db.create_connection()
    try:
        # Preparamos los %s para la consulta SQL dinámicamente
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