import io
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.services import backup_services
from app.utils.security import verificar_token

router = APIRouter(tags=["Backups"])

@router.get('/manual')
def manual_backup(token_data: dict = Depends(verificar_token)):
    # VALIDACIÓN DE SEGURIDAD: Solo el Administrador puede descargar toda la base de datos
    rol_usuario = token_data.get('nombre_rol')
    if rol_usuario != 'ADMINISTRADOR':
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado. Solo los administradores pueden generar backups."
        )

    try:
        # Ejecutamos el servicio
        res = backup_services.generar_backup_bd_memoria()
        
        # Convertimos los bytes obtenidos de pg_dump en un buffer de memoria
        buffer_memoria = io.BytesIO(res['file_bytes'])
        
        # Retornamos un StreamingResponse (Equivalente al send_file de Flask)
        return StreamingResponse(
            buffer_memoria, 
            media_type="application/sql",
            headers={"Content-Disposition": f"attachment; filename={res['file_name']}"}
        )
        
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")