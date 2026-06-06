from fastapi import APIRouter, Body, HTTPException, Depends
from app.services import vehiculos_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Vehículos"])

@router.get('/')
def get_vehiculos(token_data: dict = Depends(verificar_token)):
    if token_data.get('nombre_rol') != 'ADMINISTRADOR':
        raise HTTPException(status_code=403, detail="No tienes permisos para ver todos los vehículos.")
        
    try:
        return vehiculos_services.listar_todos_los_vehiculos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get('/mis-vehiculos')
def get_mis_vehiculos(token_data: dict = Depends(verificar_token)):
    nro_usuario = token_data.get('nro_usuario')
    try:
        return vehiculos_services.listar_mis_vehiculos(nro_usuario)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post('/')
def create_vehiculo(data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
    
    rol_autenticado = token_data.get('nombre_rol')
    
    # --- NUEVA LÓGICA DE NEGOCIO INTEGRADA ---
    if rol_autenticado == 'CLIENTE':
        # Si es cliente, ignoramos o sobreescribimos lo que mande el JSON 
        # y le asignamos directamente SU ID extraído del Token por seguridad.
        data['nro_usuario'] = token_data.get('nro_usuario')
        
    elif rol_autenticado == 'ADMINISTRADOR':
        # Si es admin, es obligatorio que el JSON declare a qué cliente va el vehículo
        if not data.get('nro_usuario'):
            raise HTTPException(
                status_code=400, 
                detail="Como ADMINISTRADOR, debe especificar el campo 'nro_usuario' para asignar el vehículo al cliente."
            )
    else:
        # Cualquier otro rol (como MECANICO) queda bloqueado
        raise HTTPException(status_code=403, detail="Tu rol no tiene permisos para registrar vehículos.")
    # ----------------------------------------

    try:
        return vehiculos_services.registrar_vehiculo(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.put('/{nro_vehiculo}')
def update_vehiculo(nro_vehiculo: int, data: dict = Body(...), token_data: dict = Depends(verificar_token)):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
        
    try:
        return vehiculos_services.actualizar_vehiculo(nro_vehiculo, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.delete('/{nro_vehiculo}')
def delete_vehiculo(nro_vehiculo: int, token_data: dict = Depends(verificar_token)):
    try:
        return vehiculos_services.borrar_vehiculo(nro_vehiculo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")