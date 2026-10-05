"""Modelo Venta del restaurante."""


class Venta:
    def __init__(self, id_venta, fecha, producto, cantidad, total, vendedor):
        self.id_venta = id_venta
        self.fecha = fecha
        self.producto = producto
        self.cantidad = int(cantidad)
        self.total = float(total)
        self.vendedor = vendedor

    def a_dict(self):
        return {"id_venta": self.id_venta, "fecha": self.fecha,
                "producto": self.producto, "cantidad": self.cantidad,
                "total": self.total, "vendedor": self.vendedor}

    @classmethod
    def desde_dict(cls, d):
        return cls(d["id_venta"], d["fecha"], d["producto"],
                   d["cantidad"], d["total"], d["vendedor"])
