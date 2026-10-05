"""Vista principal: navegación, Productos, Ventas y Usuarios (Semana 16)."""
import os
import tkinter as tk
from tkinter import ttk, messagebox

RUTA_ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
ROLES_FORMULARIO = ("Empleado", "Cliente")
DESCRIPCION_ROL = {
    "Empleado": "Empleado: atiende pedidos y registra ventas del restaurante.",
    "Cliente": "Cliente: consulta el menú y realiza pedidos.",
}


def _icono(nombre):
    return tk.PhotoImage(file=os.path.join(RUTA_ASSETS, nombre + ".png"))


def _crear_tabla(padre, columnas, alto=10):
    """Treeview con scrollbar reutilizable por todas las secciones."""
    contenedor = ttk.Frame(padre)
    tabla = ttk.Treeview(contenedor, columns=[c[0] for c in columnas],
                         show="headings", selectmode="browse", height=alto)
    for clave, texto, ancho in columnas:
        tabla.heading(clave, text=texto)
        tabla.column(clave, width=ancho, anchor="w")
    scroll = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll.set)
    tabla.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return contenedor, tabla


# ======================================================================
class ProductosFrame(ttk.Frame):
    def __init__(self, master, servicio):
        super().__init__(master, padding=15)
        self.servicio = servicio
        ttk.Label(self, text="Productos", style="Titulo.TLabel").pack(anchor="w")

        form = ttk.LabelFrame(self, text="Nuevo producto", padding=10)
        form.pack(fill="x", pady=8)
        self.vars = {k: tk.StringVar() for k in ("nombre", "categoria", "precio", "stock")}
        for i, (k, t) in enumerate((("nombre", "Nombre"), ("categoria", "Categoría"),
                                    ("precio", "Precio"), ("stock", "Stock"))):
            ttk.Label(form, text=t + ":").grid(row=0, column=i * 2, padx=4)
            ttk.Entry(form, textvariable=self.vars[k], width=14).grid(row=0, column=i * 2 + 1, padx=4)
        ttk.Button(form, text="Registrar", command=self.registrar).grid(row=0, column=8, padx=6)
        ttk.Button(form, text="Eliminar", command=self.eliminar).grid(row=0, column=9)

        cont, self.tabla = _crear_tabla(self, (("id", "ID", 50), ("nombre", "Nombre", 200),
                                               ("categoria", "Categoría", 150),
                                               ("precio", "Precio", 90), ("stock", "Stock", 80)))
        cont.pack(fill="both", expand=True)
        self.refrescar()

    def registrar(self):
        try:
            self.servicio.registrar_producto(*(self.vars[k].get() for k in
                                               ("nombre", "categoria", "precio", "stock")))
        except ValueError as e:
            messagebox.showwarning("Productos", str(e)); return
        for v in self.vars.values(): v.set("")
        self.refrescar()

    def eliminar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showinfo("Productos", "Seleccione un producto."); return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el producto seleccionado?"): return
        try:
            self.servicio.eliminar_producto(int(sel[0]))
        except ValueError as e:
            messagebox.showwarning("Productos", str(e)); return
        self.refrescar()

    def refrescar(self):
        self.tabla.delete(*self.tabla.get_children())
        for p in self.servicio.listar_productos():
            self.tabla.insert("", "end", iid=str(p.id_producto),
                              values=(p.id_producto, p.nombre, p.categoria, f"${p.precio:.2f}", p.stock))


# ======================================================================
class VentasFrame(ttk.Frame):
    def __init__(self, master, servicio, usuario_actual):
        super().__init__(master, padding=15)
        self.servicio, self.usuario_actual = servicio, usuario_actual
        ttk.Label(self, text="Ventas", style="Titulo.TLabel").pack(anchor="w")

        form = ttk.LabelFrame(self, text="Nueva venta", padding=10)
        form.pack(fill="x", pady=8)
        self.var_producto, self.var_cantidad = tk.StringVar(), tk.StringVar(value="1")
        ttk.Label(form, text="Producto:").grid(row=0, column=0, padx=4)
        self.cmb = ttk.Combobox(form, textvariable=self.var_producto, state="readonly", width=28)
        self.cmb.grid(row=0, column=1, padx=4)
        ttk.Label(form, text="Cantidad:").grid(row=0, column=2, padx=4)
        ttk.Entry(form, textvariable=self.var_cantidad, width=6).grid(row=0, column=3, padx=4)
        ttk.Button(form, text="Vender", command=self.vender).grid(row=0, column=4, padx=6)

        cont, self.tabla = _crear_tabla(self, (("id", "ID", 50), ("fecha", "Fecha", 140),
                                               ("producto", "Producto", 180), ("cantidad", "Cant.", 60),
                                               ("total", "Total", 80), ("vendedor", "Vendedor", 120)))
        cont.pack(fill="both", expand=True)
        self.refrescar()

    def _mapa_productos(self):
        return {f"{p.nombre} (stock {p.stock})": p.id_producto for p in self.servicio.listar_productos()}

    def vender(self):
        id_prod = self._mapa_productos().get(self.var_producto.get())
        try:
            v = self.servicio.registrar_venta(id_prod, self.var_cantidad.get(), self.usuario_actual.usuario)
        except ValueError as e:
            messagebox.showwarning("Ventas", str(e)); return
        messagebox.showinfo("Ventas", f"Venta registrada. Total: ${v.total:.2f}")
        self.var_cantidad.set("1"); self.refrescar()

    def refrescar(self):
        self.cmb["values"] = list(self._mapa_productos().keys())
        self.var_producto.set("")
        self.tabla.delete(*self.tabla.get_children())
        for v in self.servicio.listar_ventas():
            self.tabla.insert("", "end", iid=str(v.id_venta),
                              values=(v.id_venta, v.fecha, v.producto, v.cantidad, f"${v.total:.2f}", v.vendedor))


# ======================================================================
class UsuariosFrame(ttk.Frame):
    """Gestión de usuarios basada en eventos (Semana 16)."""

    def __init__(self, master, servicio, usuario_actual):
        super().__init__(master, padding=15)
        self.servicio = servicio
        self.usuario_actual = usuario_actual
        self.id_seleccionado = None

        ttk.Label(self, text="Gestión de usuarios", style="Titulo.TLabel").pack(anchor="w")
        self._crear_formulario()
        self._crear_tabla()
        self._vincular_eventos()
        self.refrescar_tabla()

    # ---------- construcción visual ----------
    def _crear_formulario(self):
        form = ttk.LabelFrame(self, text="Datos del usuario", padding=10)
        form.pack(fill="x", pady=8)
        self.var_nombre, self.var_usuario = tk.StringVar(), tk.StringVar()
        self.var_clave, self.var_rol = tk.StringVar(), tk.StringVar(value="Cliente")

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="e", padx=5, pady=4)
        self.ent_nombre = ttk.Entry(form, textvariable=self.var_nombre, width=30)
        self.ent_nombre.grid(row=0, column=1, padx=5)
        ttk.Label(form, text="Usuario:").grid(row=0, column=2, sticky="e", padx=5)
        self.ent_usuario = ttk.Entry(form, textvariable=self.var_usuario, width=20)
        self.ent_usuario.grid(row=0, column=3, padx=5)
        ttk.Label(form, text="Contraseña:").grid(row=1, column=0, sticky="e", padx=5, pady=4)
        self.ent_clave = ttk.Entry(form, textvariable=self.var_clave, show="*", width=30)
        self.ent_clave.grid(row=1, column=1, padx=5)
        ttk.Label(form, text="Rol:").grid(row=1, column=2, sticky="e", padx=5)
        self.cmb_rol = ttk.Combobox(form, textvariable=self.var_rol, values=ROLES_FORMULARIO,
                                    state="readonly", width=17)
        self.cmb_rol.grid(row=1, column=3, padx=5)
        self.lbl_estado = ttk.Label(form, text="Listo. Enter = registrar, Esc = limpiar.",
                                    foreground="#555")
        self.lbl_estado.grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=(6, 0))

        # command= para los botones
        botones = ttk.Frame(self)
        botones.pack(fill="x", pady=(0, 8))
        for texto, accion in (("Registrar", self.registrar), ("Actualizar", self.actualizar),
                              ("Eliminar", self.eliminar), ("Limpiar", self.limpiar)):
            ttk.Button(botones, text=texto, command=accion).pack(side="left", padx=4)

    def _crear_tabla(self):
        # La contraseña NO se incluye en el Treeview
        cont, self.tabla = _crear_tabla(self, (("id", "ID", 60), ("nombre", "Nombre", 220),
                                               ("usuario", "Usuario", 150), ("rol", "Rol", 130)))
        cont.pack(fill="both", expand=True)

    # ---------- bind(): eventos ----------
    def _vincular_eventos(self):
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar_fila)
        self.cmb_rol.bind("<<ComboboxSelected>>", self.al_cambiar_rol)
        for w in (self.ent_nombre, self.ent_usuario, self.ent_clave, self.cmb_rol):
            w.bind("<Return>", self.al_presionar_enter)
        for w in (self.ent_nombre, self.ent_usuario, self.ent_clave, self.cmb_rol, self.tabla):
            w.bind("<Escape>", self.al_presionar_escape)

    # ---------- callbacks (solo coordinan) ----------
    def al_seleccionar_fila(self, event):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        usuario = self.servicio.buscar_usuario_por_id(int(seleccion[0]))
        if usuario is None:
            return
        self.id_seleccionado = usuario.id_usuario
        self.var_nombre.set(usuario.nombre)
        self.var_usuario.set(usuario.usuario)
        self.var_clave.set("")
        self.var_rol.set(usuario.rol)
        self._mensaje(f"Editando a '{usuario.usuario}'. Contraseña vacía = conservar la actual.")

    def al_cambiar_rol(self, event):
        self._mensaje(DESCRIPCION_ROL.get(self.var_rol.get(), ""))

    def al_presionar_enter(self, event):
        self.registrar()

    def al_presionar_escape(self, event):
        self.limpiar()

    # ---------- acciones (compartidas por botones y eventos) ----------
    def registrar(self):
        try:
            self.servicio.registrar_usuario(self.var_nombre.get(), self.var_usuario.get(),
                                            self.var_clave.get(), self.var_rol.get())
        except ValueError as e:
            messagebox.showwarning("Registrar usuario", str(e)); return
        self.refrescar_tabla(); self.limpiar()
        self._mensaje("Usuario registrado correctamente.")

    def actualizar(self):
        if self.id_seleccionado is None:
            messagebox.showinfo("Actualizar", "Seleccione un usuario de la tabla."); return
        try:
            self.servicio.actualizar_usuario(self.id_seleccionado, self.var_nombre.get(),
                                             self.var_usuario.get(), self.var_clave.get(),
                                             self.var_rol.get())
        except ValueError as e:
            messagebox.showwarning("Actualizar usuario", str(e)); return
        self.refrescar_tabla(); self.limpiar()
        self._mensaje("Usuario actualizado correctamente.")

    def eliminar(self):
        if self.id_seleccionado is None:
            messagebox.showinfo("Eliminar", "Seleccione un usuario de la tabla."); return
        if not messagebox.askyesno("Confirmar", "¿Desea eliminar este usuario?"): return
        try:
            self.servicio.eliminar_usuario(self.id_seleccionado, self.usuario_actual.id_usuario)
        except ValueError as e:
            messagebox.showwarning("Eliminar usuario", str(e)); return
        self.refrescar_tabla(); self.limpiar()
        self._mensaje("Usuario eliminado.")

    def limpiar(self):
        self.var_nombre.set(""); self.var_usuario.set(""); self.var_clave.set("")
        self.var_rol.set("Cliente")
        self.id_seleccionado = None
        self.tabla.selection_remove(self.tabla.selection())
        self.ent_nombre.focus_set()
        self._mensaje("Formulario limpio.")

    def refrescar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        for u in self.servicio.listar_usuarios():
            self.tabla.insert("", "end", iid=str(u.id_usuario),
                              values=(u.id_usuario, u.nombre, u.usuario, u.rol))

    def _mensaje(self, texto):
        self.lbl_estado.config(text=texto)


# ======================================================================
class MainView(ttk.Frame):
    def __init__(self, master, servicio, usuario_actual, al_cerrar_sesion):
        super().__init__(master)
        self.servicio, self.usuario_actual = servicio, usuario_actual
        self.al_cerrar_sesion = al_cerrar_sesion
        self.iconos = {n: _icono(n) for n in ("usuarios", "productos", "ventas", "salir")}
        self.logo = tk.PhotoImage(file=os.path.join(RUTA_ASSETS, "logo.png")).subsample(3, 3)

        menu = tk.Frame(self, bg="#2c3e50", width=190)
        menu.pack(side="left", fill="y")
        menu.pack_propagate(False)
        tk.Label(menu, image=self.logo, bg="#2c3e50").pack(pady=(15, 4))
        tk.Label(menu, text=self.usuario_actual.nombre, bg="#2c3e50", fg="white",
                 font=("Segoe UI", 10, "bold"), wraplength=170).pack()
        tk.Label(menu, text=f"Rol: {self.usuario_actual.rol}", bg="#2c3e50",
                 fg="#bdc3c7").pack(pady=(0, 15))

        self._boton_menu(menu, "Productos", "productos", self.mostrar_productos)
        self._boton_menu(menu, "Ventas", "ventas", self.mostrar_ventas)
        if self.usuario_actual.es_administrador():       # control de acceso básico
            self._boton_menu(menu, "Usuarios", "usuarios", self.mostrar_usuarios)
        self._boton_menu(menu, "Cerrar sesión", "salir", self.al_cerrar_sesion, abajo=True)

        self.contenedor = ttk.Frame(self)
        self.contenedor.pack(side="left", fill="both", expand=True)
        self.mostrar_productos()

    def _boton_menu(self, menu, texto, icono, comando, abajo=False):
        b = tk.Button(menu, text="  " + texto, image=self.iconos[icono], compound="left",
                      anchor="w", bg="#34495e", fg="white", activebackground="#c0392b",
                      activeforeground="white", relief="flat", padx=12, pady=8, command=comando)
        b.pack(fill="x", padx=10, pady=3, side="bottom" if abajo else "top")

    def _mostrar(self, frame_clase, *args):
        for w in self.contenedor.winfo_children():
            w.destroy()
        frame_clase(self.contenedor, *args).pack(fill="both", expand=True)

    def mostrar_productos(self):
        self._mostrar(ProductosFrame, self.servicio)

    def mostrar_ventas(self):
        self._mostrar(VentasFrame, self.servicio, self.usuario_actual)

    def mostrar_usuarios(self):
        if not self.usuario_actual.es_administrador():   # doble verificación
            messagebox.showerror("Acceso denegado",
                                 "Solo el administrador puede gestionar usuarios.")
            return
        self._mostrar(UsuariosFrame, self.servicio, self.usuario_actual)
