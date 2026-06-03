from app.repos import auth_repos
from werkzeug.security import check_password_hash, generate_password_hash

def loguear_usuario(data: dict):
    ci = data.get('ci')
    password = data.get('password')

    if not ci or not password:
        raise ValueError("El CI y la contraseña son obligatorios.")

    usuario_db = auth_repos.obtener_usuario_por_ci(ci)

    if not usuario_db:
        raise ValueError("El usuario no existe o está inactivo.")

    password_hash = usuario_db['password_hash']

    if check_password_hash(password_hash, password):
        return {
            "success": True,
            "message": "Login exitoso",
            "usuario": {
                "nro_usuario": usuario_db['nro_usuario'],
                "ci": usuario_db['ci'],
                "nombre_completo": usuario_db['nombre_completo'],
                "correo": usuario_db['correo'],
                "nombre_rol": usuario_db['nombre_rol'],
                "telefono": usuario_db['telefono']
            },
            # "token": "aqui_iria_tu_token_jwt"
        }

    
    raise ValueError("Contraseña incorrecta.")