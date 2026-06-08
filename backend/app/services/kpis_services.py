from app.repos import kpis_repos

def generar_dashboard_general(token_data: dict):
    # Verificamos que sea parte del equipo administrativo
    rol = token_data.get('nombre_rol', '').upper()

    if rol not in ['ADMINISTRADOR', 'GERENTE TALLER']:
        raise ValueError("No tienes permisos suficientes para acceder a la analítica global.")

    # Mandamos a llamar los datos generales, sin ID de empresa
    metricas = kpis_repos.obtener_metricas_dashboard_db()

    return {
        "success": True,
        "message": "KPIs operacionales globales calculados exitosamente.",
        "data": metricas
    }