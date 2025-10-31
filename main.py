from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base
from app.routes import main_router
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Crear tablas en la base de datos
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        logger.warning("API will start but database operations may fail")

    yield

    # Shutdown: Limpiar recursos si es necesario
    logger.info("Shutting down application")

app = FastAPI(
    title="e-commerce API",
    description="""
    API para el e-commerce.

    ## Autenticación

    ### Endpoints públicos:
    - POST /api/register - Registro de nuevos usuarios
    - POST /api/login - Inicio de sesión

    ### Endpoints protegidos:
    Todos los demás endpoints requieren autenticación mediante token Bearer.
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    main_router
)


"""
app.include_router(
    books.router,
    prefix="/api/v1",
    tags=["Books"]
)
"""
# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Bookstore API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )