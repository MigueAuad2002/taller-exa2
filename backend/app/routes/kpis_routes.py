from fastapi import APIRouter, Depends, HTTPException
from app.services import kpis_services
from app.utils.security import verificar_token

router = APIRouter(prefix="/api/dashboard", tags=["Analítica y KPIs"])

@router.get('/metricas')
def get_kpis_operacionales(token_data: dict = Depends(verificar_token)):
    """
    Retorna toda la analítica general de toda la plataforma para el Dashboard.
    """
    try:
        return kpis_services.generar_dashboard_general(token_data)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular métricas: {str(e)}")