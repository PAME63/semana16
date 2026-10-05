# Restaurante App — Semana 16: Manejo de eventos en la gestión de usuarios

## Propósito
Aplicar el manejo de eventos de Tkinter (`bind()`, eventos de teclado y eventos virtuales de `ttk`) en una situación real del sistema: la **gestión de usuarios** del restaurante.

## Evolución respecto a la Semana 15
Se conserva el inicio de sesión, la navegación, Productos y Ventas. Los cambios de esta semana son:

- `modelos/usuario.py`: nuevo atributo **`rol`** (Administrador, Empleado, Cliente), persistido en `usuarios.json`.
- `servicios/restaurante_servicio.py`: nuevos métodos `listar_usuarios`, `buscar_usuario_por_id`, `registrar_usuario`, `actualizar_usuario` y `eliminar_usuario`, con todas las validaciones.
- `ui/main_view.py`: nueva clase `UsuariosFrame` (formulario + Treeview) y acceso restringido a la sección **Usuarios**.

## Estructura
```
restaurante_app/
├── datos/        productos.json · usuarios.json · ventas.json
├── modelos/      producto.py · usuario.py · venta.py
├── servicios/    archivo_servicio.py · restaurante_servicio.py
├── ui/           login_view.py · main_view.py
├── assets/       logo.png · íconos del menú
├── main.py
└── README.md
```

## Roles
| Rol | Acceso |
|---|---|
| Administrador | Productos, Ventas y **gestión de usuarios** (crea/edita/elimina Empleados y Clientes) |
| Empleado | Productos y Ventas |
| Cliente | Productos y Ventas |

Las cuentas de administrador no se editan ni se eliminan desde la interfaz, y la cuenta con la sesión activa nunca puede eliminarse. No hay sistema de permisos avanzado.

## Eventos implementados
| Evento | Widget | Callback | Resultado |
|---|---|---|---|
| `<<TreeviewSelect>>` | Treeview | `al_seleccionar_fila` | Carga el usuario seleccionado en el formulario |
| `<Return>` | Entradas y Combobox | `al_presionar_enter` | Llama a `registrar()` |
| `<Escape>` | Formulario y tabla | `al_presionar_escape` | Llama a `limpiar()` |
| `<<ComboboxSelected>>` | Combobox de rol | `al_cambiar_rol` | Muestra la descripción del rol elegido |

### `bind()`, `command=` y callbacks
- **`command=`** se usa en los botones Registrar, Actualizar, Eliminar y Limpiar: la acción se dispara con un clic.
- **`bind()`** asocia un *evento* (selección, tecla, cambio de opción) con una función; la función recibe un objeto `event`.
- **Callback**: función que Tkinter invoca cuando ocurre el evento. Los callbacks de esta app solo coordinan: `<Return>` reutiliza `registrar()` y `<Escape>` reutiliza `limpiar()`, sin duplicar lógica.

Flujo: *interacción → evento → bind() → callback → RestauranteServicio → usuarios.json → Treeview actualizado*.

El Treeview muestra solo ID, nombre, usuario y rol. La contraseña nunca se muestra; al seleccionar una fila se consulta el objeto por su ID mediante `RestauranteServicio`. Al actualizar, una contraseña vacía conserva la actual.

## Persistencia
`RestauranteServicio` usa `ArchivoServicio` para leer y escribir `usuarios.json`. `main_view.py` no accede a archivos JSON.

## Ejecución
Requiere Python 3.10+ con Tkinter.
```
cd restaurante_app
python main.py
```
Usuarios de prueba:

| Usuario | Contraseña | Rol |
|---|---|---|
| admin | admin123 | Administrador |
| mperez | 1234 | Empleado |
| cloor | 1234 | Cliente |

## Pruebas realizadas
Verificadas con una prueba automática de la interfaz: inicio de sesión; registro con Enter; selección con `<<TreeviewSelect>>`; actualización; eliminación con confirmación; bloqueo de la cuenta activa; limpieza con Escape; evento del Combobox; rechazo de usuarios duplicados; persistencia tras reiniciar; acceso a Usuarios solo para el administrador; Productos y Ventas.
