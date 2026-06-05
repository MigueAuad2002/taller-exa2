import jwt
from datetime import datetime,timedelta,timezone
from app.config import Config
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

def create_access_token(nro_usuario, username, nombre_rol, id_empresa, nombre_completo, minutes=120):
    """
    GENERA EL JWT PARA LA SESIÓN DEL USUARIO
    """
    payload = {
        'nro_usuario': nro_usuario,
        'username': username,
        'nombre_rol': nombre_rol,
        'id_empresa': id_empresa,  # ¡Ahora sí está incluido en el token!
        'nombre_completo': nombre_completo,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=minutes),
        'iat': datetime.now(timezone.utc)
    }

    # Usamos Config.TOKEN_KEY que definiste en tu archivo de configuración
    return jwt.encode(payload, Config.TOKEN_KEY, algorithm="HS256")


def decode_access_token(token: str):
    """
    DECODIFICA Y VALIDA EL JWT ENVIADO POR EL FRONTEND
    """
    try:
        payload = jwt.decode(token, Config.TOKEN_KEY, algorithms=["HS256"])
        
        return {
            'success': True,
            'message': 'TOKEN VALIDO',
            'payload': payload
        }
        
    except jwt.ExpiredSignatureError:
        return {
            'success': False,
            'message': 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.'
        }
        
    except jwt.InvalidTokenError:
        return {
            'success': False,
            'message': 'Token de acceso inválido o corrupto.'
        }



# Inicializamos el manejador Bearer de FastAPI
bearer_scheme = HTTPBearer()

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Dependencia reusable que extrae el token Bearer, lo valida con tu función 
    y retorna el payload decodificado si todo está correcto.
    """
    token = credentials.credentials
    resultado = decode_access_token(token)
    
    # Evaluamos las llaves exactas que tiene tu función decode_access_token
    if not resultado.get('success'):
        raise HTTPException(status_code=401, detail=resultado.get('message'))
        
    # Si es válido, retornamos el payload de tu JWT (id_empresa, nombre_rol, etc.)
    return resultado.get('payload')