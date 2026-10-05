"""Modelo Usuario con rol (Semana 16)."""

ROL_ADMINISTRADOR = "Administrador"
ROL_EMPLEADO = "Empleado"
ROL_CLIENTE = "Cliente"
ROLES = (ROL_ADMINISTRADOR, ROL_EMPLEADO, ROL_CLIENTE)


class Usuario:
    def __init__(self, id_usuario, nombre, usuario, contrasena, rol=ROL_CLIENTE):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.usuario = usuario
        self.contrasena = contrasena
        self.rol = rol

    def es_administrador(self):
        return self.rol == ROL_ADMINISTRADOR

    def a_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "usuario": self.usuario,
            "contrasena": self.contrasena,
            "rol": self.rol,
        }

    @classmethod
    def desde_dict(cls, d):
        return cls(d["id_usuario"], d["nombre"], d["usuario"],
                   d["contrasena"], d.get("rol", ROL_CLIENTE))
