"""Vista de inicio de sesión."""
import os
import tkinter as tk
from tkinter import ttk, messagebox

RUTA_ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")


class LoginView(ttk.Frame):
    def __init__(self, master, servicio, al_autenticar):
        super().__init__(master, padding=30)
        self.servicio = servicio
        self.al_autenticar = al_autenticar

        self.logo = tk.PhotoImage(file=os.path.join(RUTA_ASSETS, "logo.png"))
        ttk.Label(self, image=self.logo).pack(pady=(10, 5))
        ttk.Label(self, text="Restaurante App", style="Titulo.TLabel").pack()
        ttk.Label(self, text="Inicie sesión para continuar").pack(pady=(0, 15))

        self.var_usuario = tk.StringVar()
        self.var_clave = tk.StringVar()
        ttk.Label(self, text="Usuario").pack(anchor="w")
        self.ent_usuario = ttk.Entry(self, textvariable=self.var_usuario, width=30)
        self.ent_usuario.pack(pady=(0, 8))
        ttk.Label(self, text="Contraseña").pack(anchor="w")
        self.ent_clave = ttk.Entry(self, textvariable=self.var_clave, show="*", width=30)
        self.ent_clave.pack(pady=(0, 12))
        ttk.Button(self, text="Ingresar", command=self.iniciar_sesion).pack(fill="x")

        # Evento: Enter en los campos también inicia sesión (reutiliza el método)
        self.ent_usuario.bind("<Return>", lambda e: self.iniciar_sesion())
        self.ent_clave.bind("<Return>", lambda e: self.iniciar_sesion())
        self.ent_usuario.focus_set()

    def iniciar_sesion(self):
        usuario = self.servicio.autenticar(self.var_usuario.get(), self.var_clave.get())
        if usuario is None:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")
            self.var_clave.set("")
            return
        self.al_autenticar(usuario)
