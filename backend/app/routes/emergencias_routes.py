from fastapi import APIRouter, Body, HTTPException, Depends
from app.services import emergencias_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Emergencias"])

ROLES_ADMIN_CLIENTE = ['ADMINISTRADOR', 'CLIENTE']
ROLES_MECANICO = ['MECANICO', 'MECÁNICO', 'TECNICO', 'TÉCNICO']
ROLES_ACTUALIZAR = ROLES_ADMIN_CLIENTE + ROLES_MECANICO

def normalizar_rol(rol_usuario: str):
    return rol_usuario.strip().upper() if rol_usuario else ""

def validar_acceso_emergencias(rol_usuario: str):
    rol_usuario = normalizar_rol(rol_usuario)
    if rol_usuario not in ROLES_ADMIN_CLIENTE:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para gestionar o reportar emergencias."
        )

# --- RUTAS GET (LECTURA) ---

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

# --- RUTAS POST/PUT/DELETE (ESCRITURA) ---

@router.post('/')
def create_emergencia(data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    # Mecánicos no pueden crear emergencias
    if normalizar_rol(token_data.get('nombre_rol')) not in ROLES_ADMIN_CLIENTE:
        raise HTTPException(status_code=403, detail="Tu rol no tiene permisos para crear emergencias.")
        
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')

    try:
        # Enviamos token_data para que el servicio aplique las reglas
        return emergencias_services.registrar_emergencia(data, token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.put('/{nro_emergencia}')
def update_emergencia(nro_emergencia: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    # Admin, Cliente y Mecánico pueden entrar, pero el servicio restringe qué puede tocar cada uno
    if normalizar_rol(token_data.get('nombre_rol')) not in ROLES_ACTUALIZAR:
        raise HTTPException(status_code=403, detail="No tienes permisos para actualizar emergencias.")

    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')

    try:
        return emergencias_services.actualizar_emergencia(nro_emergencia, data, token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.delete('/{nro_emergencia}')
def delete_emergencia(nro_emergencia: int, token_data: dict = Depends(verificar_token)):
    # Bloqueamos estrictamente a los mecánicos
    if normalizar_rol(token_data.get('nombre_rol')) not in ROLES_ADMIN_CLIENTE:
        raise HTTPException(status_code=403, detail="Tu rol no tiene permisos para eliminar emergencias.")

    try:
        return emergencias_services.borrar_emergencia(nro_emergencia, token_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")