from fastapi import APIRouter, Body, HTTPException
from app.services import users_services

router = APIRouter(tags=["Usuarios"])

@router.get('/')
def get_users():
    try:
        return users_services.listar_usuarios()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post('/')
def create_user(data: dict = Body(...)):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
    
    try:
        return users_services.registrar_usuario(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.put('/{nro_usuario}')
def update_user(nro_usuario: int, data: dict = Body(...)):
    if not data:
        raise HTTPException(status_code=400, detail='El cuerpo de la petición está vacío.')
        
    try:
        return users_services.actualizar_usuario(nro_usuario, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")

@router.delete('/{nro_usuario}')
def delete_user(nro_usuario: int):
    try:
        return users_services.borrar_usuario(nro_usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en BD: {str(e)}")