"""Configuración de la aplicación."""

import os
from dotenv import load_dotenv

load_dotenv()


class Configuracion:
    """Configuración general de la aplicación."""

    base_datos: str = os.environ["DATABASE_URL"]


CONFIGURACION = Configuracion()