import uvicorn
from app import create_app

# Instanciamos la aplicación llamando a la fábrica
app = create_app()

if __name__ == "__main__":
    
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)