"""Reglas de negocio y persistencia del restaurante."""
import os
from datetime import datetime

from modelos.producto import Producto
from modelos.usuario import Usuario, ROL_EMPLEADO, ROL_CLIENTE
from modelos.venta import Venta
from servicios.archivo_servicio import ArchivoServicio

ROLES_GESTIONABLES = (ROL_EMPLEADO, ROL_CLIENTE)


class RestauranteServicio:
    def __init__(self, carpeta_datos):
        self.ruta_productos = os.path.join(carpeta_datos, "productos.json")
        self.ruta_usuarios = os.path.join(carpeta_datos, "usuarios.json")
        self.ruta_ventas = os.path.join(carpeta_datos, "ventas.json")
        self.productos = [Producto.desde_dict(d)
                          for d in ArchivoServicio.leer_json(self.ruta_productos)]
        self.usuarios = [Usuario.desde_dict(d)
                         for d in ArchivoServicio.leer_json(self.ruta_usuarios)]
        self.ventas = [Venta.desde_dict(d)
                       for d in ArchivoServicio.leer_json(self.ruta_ventas)]

    # ---------------- persistencia ----------------
    def _guardar_productos(self):
        ArchivoServicio.guardar_json(self.ruta_productos,
                                     [p.a_dict() for p in self.productos])

    def _guardar_usuarios(self):
        ArchivoServicio.guardar_json(self.ruta_usuarios,
                                     [u.a_dict() for u in self.usuarios])

    def _guardar_ventas(self):
        ArchivoServicio.guardar_json(self.ruta_ventas,
                                     [v.a_dict() for v in self.ventas])

    # ---------------- autenticación ----------------
    def autenticar(self, usuario, contrasena):
        for u in self.usuarios:
            if u.usuario == usuario.strip() and u.contrasena == contrasena:
                return u
        return None

    # ---------------- productos ----------------
    def listar_productos(self):
        return list(self.productos)

    def buscar_producto_por_id(self, id_producto):
        return next((p for p in self.productos if p.id_producto == id_producto), None)

    def registrar_producto(self, nombre, categoria, precio, stock):
        if not nombre.strip() or not categoria.strip():
            raise ValueError("Nombre y categoría son obligatorios.")
        try:
            precio = float(precio)
            stock = int(stock)
        except ValueError:
            raise ValueError("Precio y stock deben ser numéricos.")
        if precio <= 0 or stock < 0:
            raise ValueError("Precio debe ser mayor a 0 y stock no negativo.")
        nuevo_id = max((p.id_producto for p in self.productos), default=0) + 1
        prod = Producto(nuevo_id, nombre.strip(), categoria.strip(), precio, stock)
        self.productos.append(prod)
        self._guardar_productos()
        return prod

    def eliminar_producto(self, id_producto):
        prod = self.buscar_producto_por_id(id_producto)
        if prod is None:
            raise ValueError("El producto no existe.")
        self.productos.remove(prod)
        self._guardar_productos()

    # ---------------- ventas ----------------
    def listar_ventas(self):
        return list(self.ventas)

    def registrar_venta(self, id_producto, cantidad, vendedor):
        prod = self.buscar_producto_por_id(id_producto)
        if prod is None:
            raise ValueError("Seleccione un producto válido.")
        try:
            cantidad = int(cantidad)
        except ValueError:
            raise ValueError("La cantidad debe ser un número entero.")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
        if cantidad > prod.stock:
            raise ValueError(f"Stock insuficiente (disponible: {prod.stock}).")
        prod.stock -= cantidad
        nuevo_id = max((v.id_venta for v in self.ventas), default=0) + 1
        venta = Venta(nuevo_id, datetime.now().strftime("%Y-%m-%d %H:%M"),
                      prod.nombre, cantidad, prod.precio * cantidad, vendedor)
        self.ventas.append(venta)
        self._guardar_productos()
        self._guardar_ventas()
        return venta

    # ---------------- usuarios (Semana 16) ----------------
    def listar_usuarios(self):
        return list(self.usuarios)

    def buscar_usuario_por_id(self, id_usuario):
        return next((u for u in self.usuarios if u.id_usuario == id_usuario), None)

    def _validar_datos_usuario(self, nombre, usuario, contrasena, rol,
                               id_excluir=None, exigir_clave=True):
        if not nombre.strip() or not usuario.strip():
            raise ValueError("Nombre y usuario son obligatorios.")
        if exigir_clave and not contrasena.strip():
            raise ValueError("La contraseña es obligatoria.")
        if rol not in ROLES_GESTIONABLES:
            raise ValueError("El rol debe ser Empleado o Cliente.")
        for u in self.usuarios:
            if (u.usuario.lower() == usuario.strip().lower()
                    and u.id_usuario != id_excluir):
                raise ValueError("Ese nombre de usuario ya existe.")

    def registrar_usuario(self, nombre, usuario, contrasena, rol):
        self._validar_datos_usuario(nombre, usuario, contrasena, rol)
        nuevo_id = max((u.id_usuario for u in self.usuarios), default=0) + 1
        nuevo = Usuario(nuevo_id, nombre.strip(), usuario.strip(), contrasena, rol)
        self.usuarios.append(nuevo)
        self._guardar_usuarios()
        return nuevo

    def actualizar_usuario(self, id_usuario, nombre, usuario, contrasena, rol):
        existente = self.buscar_usuario_por_id(id_usuario)
        if existente is None:
            raise ValueError("El usuario no existe.")
        if existente.es_administrador():
            raise ValueError("Las cuentas de administrador no se editan desde aquí.")
        self._validar_datos_usuario(nombre, usuario, contrasena, rol,
                                    id_excluir=id_usuario, exigir_clave=False)
        existente.nombre = nombre.strip()
        existente.usuario = usuario.strip()
        existente.rol = rol
        if contrasena.strip():
            existente.contrasena = contrasena
        self._guardar_usuarios()

    def eliminar_usuario(self, id_usuario, id_usuario_actual):
        if id_usuario == id_usuario_actual:
            raise ValueError("No puede eliminar la cuenta con la que inició sesión.")
        existente = self.buscar_usuario_por_id(id_usuario)
        if existente is None:
            raise ValueError("El usuario no existe.")
        if existente.es_administrador():
            raise ValueError("No se puede eliminar una cuenta de administrador.")
        self.usuarios.remove(existente)
        self._guardar_usuarios()
