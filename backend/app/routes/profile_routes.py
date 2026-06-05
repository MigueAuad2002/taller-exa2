from fastapi import APIRouter,Body,HTTPException
from app.services import profile_services

router=APIRouter(tags=['Perfil'])

@router.get('/')
def get_profile():
    try:
        return profile_services.obtener_perfil_usuario(12)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error interno en : {err}")