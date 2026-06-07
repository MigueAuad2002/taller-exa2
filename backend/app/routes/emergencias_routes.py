from fastapi import APIRouter, Body, HTTPException, Depends
from app.services import emergencias_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Emergencias"])

ROLES_PERMITIDOS = ['ADMINISTRADOR', 'CLIENTE']
ROLES_MECANICO = ['MECANICO', 'MECÁNICO', 'TECNICO', 'TÉCNICO']


def normalizar_rol(rol_usuario: str):
    return rol_usuario.strip().upper() if rol_usuario else ""


def validar_acceso_emergencias(rol_usuario: str):
    rol_usuario = normalizar_rol(rol_usuario)

    if rol_usuario not in ROLES_PERMITIDOS:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para gestionar o reportar emergencias."
        )


@router.get('/')
def get_todas_las_emergencias(token_data: dict = Depends(verificar_token)):
    if normalizar_rol(token_data.get('nombre_rol')) != 'ADMINISTRADOR':
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden ver el listado global de emergencias."
        )

    try:
        return emergencias_services.listar_todas_las_emergencias()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get('/mis-emergencias')
def get_mis_emergencias(token_data: dict = Depends(verificar_token)):
    validar_acceso_emergencias(token_data.get('nombre_rol'))

    nro_usuario = token_data.get('nro_usuario')

    try:
        return emergencias_services.listar_mis_emergencias(nro_usuario)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get('/mi-taller')
def get_emergencias_mi_taller(token_data: dict = Depends(verificar_token)):
    rol_usuario = normalizar_rol(token_data.get('nombre_rol'))

    if rol_usuario not in ROLES_MECANICO:
        raise HTTPException(
            status_code=403,
            detail="Solo los mecánicos pueden ver las emergencias de su taller."
        )

    nro_usuario = token_data.get('nro_usuario')

    try:
        return emergencias_services.listar_emergencias_mi_taller(nro_usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post('/')
def create_emergencia(data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    rol_autenticado = normalizar_rol(token_data.get('nombre_rol'))
    validar_acceso_emergencias(rol_autenticado)

    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')

    if rol_autenticado == 'CLIENTE':
        data['nro_usuario'] = token_data.get('nro_usuario')
    elif rol_autenticado == 'ADMINISTRADOR':
        if not data.get('nro_usuario'):
            raise HTTPException(
                status_code=400,
                detail="Como ADMINISTRADOR, debe especificar el campo 'nro_usuario' del cliente afectado."
            )

    try:
        return emergencias_services.registrar_emergencia(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")


@router.put('/{nro_emergencia}')
def update_emergencia(nro_emergencia: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    validar_acceso_emergencias(token_data.get('nombre_rol'))

    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')

    try:
        return emergencias_services.actualizar_emergencia(nro_emergencia, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")


@router.delete('/{nro_emergencia}')
def delete_emergencia(nro_emergencia: int, token_data: dict = Depends(verificar_token)):
    if normalizar_rol(token_data.get('nombre_rol')) != 'ADMINISTRADOR':
        raise HTTPException(
            status_code=403,
            detail="Solo un administrador puede borrar un registro físico de emergencia."
        )

    try:
        return emergencias_services.borrar_emergencia(nro_emergencia)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")