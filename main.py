from contextlib import asynccontextmanager

from fastapi import FastAPI

from nucleo.configuracion import CONFIGURACION
from nucleo.conexion import conexion
from presentacion.rutas.productos import router as productos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conexion.conectar(CONFIGURACION.base_datos)

    yield

    await conexion.cerrar()


app = FastAPI(lifespan=lifespan)

app.include_router(productos_router)