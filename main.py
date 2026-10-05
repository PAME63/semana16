"""Punto de entrada de restaurante_app (Semana 16)."""
import os
import tkinter as tk
from tkinter import ttk

from servicios.restaurante_servicio import RestauranteServicio
from ui.login_view import LoginView
from ui.main_view import MainView

BASE = os.path.dirname(os.path.abspath(__file__))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Restaurante App")
        self.geometry("420x520")
        self.servicio = RestauranteServicio(os.path.join(BASE, "datos"))
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 16, "bold"), foreground="#c0392b")
        self.vista = None
        self.mostrar_login()

    def _cambiar_vista(self, vista):
        if self.vista is not None:
            self.vista.destroy()
        self.vista = vista
        self.vista.pack(fill="both", expand=True)

    def mostrar_login(self):
        self.geometry("420x520")
        self._cambiar_vista(LoginView(self, self.servicio, self.mostrar_principal))

    def mostrar_principal(self, usuario):
        self.geometry("980x580")
        self._cambiar_vista(MainView(self, self.servicio, usuario, self.mostrar_login))


if __name__ == "__main__":
    App().mainloop()
