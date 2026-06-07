from fastapi import APIRouter, Body, HTTPException, Depends
from app.services import talleres_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Talleres"])

# Lista global de roles autorizados para este módulo
ROLES_PERMITIDOS = ['ADMINISTRADOR', 'GERENTE TALLER']

def validar_rol_taller(rol_usuario: str):
    if rol_usuario not in ROLES_PERMITIDOS:
        raise HTTPException(status_code=403, detail="No tienes permisos para gestionar talleres.")

@router.get('/')
def get_talleres(token_data: dict = Depends(verificar_token)):
    validar_rol_taller(token_data.get('nombre_rol'))
    try:
        return talleres_services.listar_talleres()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post('/')
def create_taller(data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    validar_rol_taller(token_data.get('nombre_rol'))
    
    # Lógica inteligente: Si es un Gerente, forzamos que el taller se cree en su propia empresa
    if token_data.get('nombre_rol') == 'GERENTE TALLER':
        data['id_empresa'] = token_data.get('id_empresa')

    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
    
    try:
        return talleres_services.registrar_taller(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.put('/{nro_taller}')
def update_taller(nro_taller: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    validar_rol_taller(token_data.get('nombre_rol'))
    
    if token_data.get('nombre_rol') == 'GERENTE TALLER':
        data['id_empresa'] = token_data.get('id_empresa')

    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
        
    try:
        return talleres_services.actualizar_taller(nro_taller, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.delete('/{nro_taller}')
def delete_taller(nro_taller: int, token_data: dict = Depends(verificar_token)):
    validar_rol_taller(token_data.get('nombre_rol'))
    
    try:
        return talleres_services.borrar_taller(nro_taller)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")
    
# =================================================================
#                   RUTAS DE SERVICIOS DEL TALLER
# =================================================================

@router.get('/{nro_taller}/servicios')
def get_servicios_taller(nro_taller: int, token_data: dict = Depends(verificar_token)):
    validar_rol_taller(token_data.get('nombre_rol'))
    try:
        return talleres_services.listar_servicios_taller(nro_taller)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post('/{nro_taller}/servicios')
def create_servicio_taller(nro_taller: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    validar_rol_taller(token_data.get('nombre_rol'))
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
        
    try:
        return talleres_services.registrar_servicio_taller(nro_taller, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.put('/{nro_taller}/servicios/{nro_servicio}')
def update_servicio_taller(nro_taller: int, nro_servicio: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    validar_rol_taller(token_data.get('nombre_rol'))
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
        
    try:
        return talleres_services.actualizar_servicio_taller(nro_servicio, nro_taller, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.delete('/{nro_taller}/servicios/{nro_servicio}')
def delete_servicio_taller(nro_taller: int, nro_servicio: int, token_data: dict = Depends(verificar_token)):
    validar_rol_taller(token_data.get('nombre_rol'))
    try:
        return talleres_services.borrar_servicio_taller(nro_servicio, nro_taller)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")