from app.classes.postgres import PostgreSQL
from app.config import Config

def obtener_usuario_por_ci(ci: str):
    db = PostgreSQL()
    db.create_connection()
    
    try:
        query = f"""
            SELECT 
                a.password_hash, 
                a.nro_usuario, 
                a.ci, 
                b.nombre_completo, 
                b.correo, 
                b.telefono, 
                a.nombre_usuario, 
                c.nombre_rol
            FROM {Config.SCHEMA}.usuario a
            INNER JOIN taller.persona b ON a.ci = b.ci
            INNER JOIN taller.rol c ON a.nro_rol = c.nro_rol
            WHERE a.ci = %s AND a.estado = 'ACTIVO';
        """
        
        
        resultado = db.execute_query(query, (ci,), fetchone=True)
        
        if resultado:
            return {
                "password_hash": resultado[0],
                "nro_usuario": resultado[1],
                "ci": resultado[2],
                "nombre_completo": resultado[3],
                "correo": resultado[4],
                "telefono": resultado[5],
                "nombre_usuario": resultado[6],
                "nombre_rol": resultado[7]
            }
            
        return None
        
    finally:
        db.close_connection()