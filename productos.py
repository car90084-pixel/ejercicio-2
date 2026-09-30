from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from nucleo.conexion import ConexionDep
from dominio.repositorios import (
    obtener_producto,
    obtener_productos,
    actualizar_producto,
    eliminar_producto,
)
from dominio.esquemas import ProductoActualizar

router = APIRouter(tags=["productos"])

templates = Jinja2Templates(directory="presentacion/templates")


@router.get("/productos")
async def listar_productos(request: Request, conn: ConexionDep):
    productos = await obtener_productos(conn)
    return templates.TemplateResponse(
        request=request,
        name="productos.html",
        context={"productos": productos},
    )


@router.get("/productos/{producto_id}/editar")
async def editar_producto_vista(
    request: Request,
    conn: ConexionDep,
    producto_id: int,
):
    producto = await obtener_producto(conn, producto_id)

    if producto is None:
        return templates.TemplateResponse(
            request=request,
            name="componentes/producto_no_encontrado.html",
            context={"producto_id": producto_id},
        )

    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_editar.html",
        context={
            "producto": producto,
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "cantidad": producto["cantidad"],
            "descripcion": producto["descripcion"],
            "errores": {},
        },
    )


@router.get("/productos/{producto_id}/cancelar")
async def cancelar_edicion_vista(
    request: Request,
    conn: ConexionDep,
    producto_id: int,
):
    producto = await obtener_producto(conn, producto_id)

    if producto is None:
        return templates.TemplateResponse(
            request=request,
            name="componentes/producto_no_encontrado.html",
            context={"producto_id": producto_id},
        )

    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_producto.html",
        context={"producto": producto},
    )


@router.post("/productos/{producto_id}")
async def guardar_producto_vista(
    request: Request,
    conn: ConexionDep,
    producto_id: int,
    nombre: Annotated[str | None, Form()] = None,
    precio: Annotated[str | None, Form()] = None,
    cantidad: Annotated[str | None, Form()] = None,
    descripcion: Annotated[str | None, Form()] = None,
):
    producto = await obtener_producto(conn, producto_id)

    if producto is None:
        return templates.TemplateResponse(
            request=request,
            name="componentes/producto_no_encontrado.html",
            context={"producto_id": producto_id},
        )

    errores = {}

    try:
        precio_numero = float(precio) if precio not in (None, "") else None
    except ValueError:
        precio_numero = None
        errores["precio"] = "El precio debe ser un número válido."

    try:
        cantidad_numero = int(cantidad) if cantidad not in (None, "") else None
    except ValueError:
        cantidad_numero = None
        errores["cantidad"] = "La cantidad debe ser un número entero."

    if not errores:
        try:
            datos = ProductoActualizar(
                nombre=nombre,
                precio=precio_numero,
                cantidad=cantidad_numero,
                descripcion=descripcion,
            )
        except ValidationError as error:
            for problema in error.errors():
                campo = problema["loc"][0]
                errores[campo] = problema["msg"]

    if errores:
        response = templates.TemplateResponse(
            request=request,
            name="componentes/fila_editar.html",
            context={
                "producto": producto,
                "nombre": nombre,
                "precio": precio,
                "cantidad": cantidad,
                "descripcion": descripcion,
                "errores": errores,
            },
        )
        response.status_code = 422
        return response

    actualizado = await actualizar_producto(
        conn,
        producto_id,
        datos.nombre,
        datos.precio,
        datos.cantidad,
        datos.descripcion,
    )

    if not actualizado:
        return templates.TemplateResponse(
            request=request,
            name="componentes/producto_no_encontrado.html",
            context={"producto_id": producto_id},
        )

    producto_actualizado = await obtener_producto(conn, producto_id)

    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_actualizada.html",
        context={"producto": producto_actualizado},
    )


@router.delete("/productos/{producto_id}")
async def eliminar_producto_vista(
    request: Request,
    conn: ConexionDep,
    producto_id: int,
):
    eliminado = await eliminar_producto(conn, producto_id)

    if not eliminado:
        return templates.TemplateResponse(
            request=request,
            name="componentes/producto_no_encontrado.html",
            context={"producto_id": producto_id},
        )

    return templates.TemplateResponse(
        request=request,
        name="componentes/fila_eliminada.html",
        context={"producto_id": producto_id},
    )