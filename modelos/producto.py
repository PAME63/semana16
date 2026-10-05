"""Modelo Producto del restaurante."""


class Producto:
    def __init__(self, id_producto, nombre, categoria, precio, stock):
        self.id_producto = id_producto
        self.nombre = nombre
        self.categoria = categoria
        self.precio = float(precio)
        self.stock = int(stock)

    def a_dict(self):
        return {"id_producto": self.id_producto, "nombre": self.nombre,
                "categoria": self.categoria, "precio": self.precio,
                "stock": self.stock}

    @classmethod
    def desde_dict(cls, d):
        return cls(d["id_producto"], d["nombre"], d["categoria"],
                   d["precio"], d["stock"])
