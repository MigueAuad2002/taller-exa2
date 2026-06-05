from app.repos import profile_repos
from app.utils import security

def obtener_perfil_usuario(nro_usuario):

    if not nro_usuario:
        raise ValueError('Debe Estar Logueado para ver su perfil.')
    
    usuario_db=profile_repos.get_profile(nro_usuario)

    if not usuario_db:
        raise ValueError('El usuario no se encuentra registrado en el Sistema.')
    
    return {
        'success':True,
        'message':'Datos del Usuario Obtenido Exitosamente',
        'data':usuario_db
    }