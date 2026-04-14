"""
╔══════════════════════════════════════════════════════════════════════════╗
║           SISTEMA DE RECURSOS HUMANOS — Python + Tkinter + SQLite       ║
║                        Abraham Ramos — Full Stack                       ║
╚══════════════════════════════════════════════════════════════════════════╝

DESCRIPCIÓN:
    Sistema de gestión de empleados con interfaz gráfica moderna.
    Guarda todos los datos en una base de datos SQLite local.

CÓMO EJECUTAR:
    python rrhh.py
    (tkinter viene incluido con Python, no requiere instalación extra)

FUNCIONALIDADES:
    ✅ Registro de empleados (nombre, puesto, depto, salario, fecha ingreso)
    ✅ Listado con búsqueda en tiempo real
    ✅ Edición y eliminación de empleados
    ✅ Dashboard con estadísticas (total, nómina, por departamento)
    ✅ Exportar reporte a archivo .txt
    ✅ Interfaz oscura moderna con colores por departamento
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
from datetime import datetime


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  PALETA DE COLORES — Tema oscuro profesional                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

COLORES = {
    "bg_dark":     "#0f1117",   # Fondo principal
    "bg_panel":    "#1a1d2e",   # Paneles y tarjetas
    "bg_card":     "#252840",   # Tarjetas de estadísticas
    "bg_input":    "#1e2133",   # Campos de entrada
    "accent":      "#6c63ff",   # Acento principal (morado)
    "accent2":     "#00d4aa",   # Acento secundario (verde-cian)
    "danger":      "#ff4757",   # Rojo para eliminar
    "warning":     "#ffa502",   # Naranja para editar
    "success":     "#2ed573",   # Verde para confirmar
    "text":        "#e8eaf0",   # Texto principal
    "text_dim":    "#8b8fa8",   # Texto secundario
    "border":      "#2e3250",   # Bordes
    "row_alt":     "#1e2133",   # Filas alternadas en tabla
    "header_bg":   "#252840",   # Fondo de encabezados tabla
}

# Colores por departamento (para la tabla y el dashboard)
DEPT_COLORS = {
    "Tecnología":   "#6c63ff",
    "Ventas":       "#00d4aa",
    "Finanzas":     "#ffa502",
    "RRHH":         "#ff6b9d",
    "Operaciones":  "#3d9cff",
    "Marketing":    "#ff7f50",
    "Legal":        "#a29bfe",
    "Otro":         "#8b8fa8",
}

DEPARTAMENTOS = list(DEPT_COLORS.keys())
PUESTOS = [
    "Gerente", "Director", "Coordinador", "Analista",
    "Desarrollador", "Diseñador", "Vendedor", "Contador",
    "Recursos Humanos", "Operador", "Auxiliar", "Otro"
]


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  BASE DE DATOS — SQLite                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class Database:
    """
    Maneja toda la interacción con SQLite.
    Usa una sola tabla 'empleados' con todos los campos relevantes.
    """

    def __init__(self, db_path="rrhh.db"):
        self.db_path = db_path
        self.conn    = sqlite3.connect(db_path)
        # row_factory permite acceder a columnas por nombre (fila["nombre"])
        self.conn.row_factory = sqlite3.Row
        self._crear_tabla()
        self._insertar_datos_demo()

    def _crear_tabla(self):
        """Crea la tabla de empleados si no existe."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS empleados (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre        TEXT    NOT NULL,
                apellido      TEXT    NOT NULL,
                puesto        TEXT    NOT NULL,
                departamento  TEXT    NOT NULL,
                email         TEXT    UNIQUE,
                telefono      TEXT,
                salario       REAL    NOT NULL DEFAULT 0,
                fecha_ingreso TEXT    NOT NULL,
                activo        INTEGER NOT NULL DEFAULT 1,
                notas         TEXT
            )
        """)
        self.conn.commit()

    def _insertar_datos_demo(self):
        """Inserta empleados de ejemplo si la tabla está vacía."""
        count = self.conn.execute("SELECT COUNT(*) FROM empleados").fetchone()[0]
        if count > 0:
            return

        demo = [
            ("Ana",      "García",    "Gerente",      "Tecnología",   "ana.garcia@empresa.com",    "8112345678", 45000, "2021-03-15"),
            ("Carlos",   "López",     "Desarrollador","Tecnología",   "carlos.lopez@empresa.com",  "8119876543", 32000, "2022-06-01"),
            ("María",    "Hernández", "Analista",     "Finanzas",     "maria.h@empresa.com",       "8118765432", 28000, "2021-11-20"),
            ("Roberto",  "Martínez",  "Vendedor",     "Ventas",       "roberto.m@empresa.com",     "8117654321", 22000, "2023-01-10"),
            ("Sofía",    "Ramírez",   "Coordinador",  "RRHH",         "sofia.r@empresa.com",       "8116543210", 30000, "2020-08-05"),
            ("Diego",    "Torres",    "Diseñador",    "Marketing",    "diego.t@empresa.com",       "8115432109", 27000, "2022-09-14"),
            ("Valentina","Flores",    "Contador",     "Finanzas",     "valentina.f@empresa.com",   "8114321098", 31000, "2021-04-22"),
            ("Miguel",   "Sánchez",   "Director",     "Operaciones",  "miguel.s@empresa.com",      "8113210987", 55000, "2019-12-01"),
        ]
        self.conn.executemany("""
            INSERT INTO empleados
            (nombre, apellido, puesto, departamento, email, telefono, salario, fecha_ingreso)
            VALUES (?,?,?,?,?,?,?,?)
        """, demo)
        self.conn.commit()

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def obtener_todos(self, busqueda="", departamento="Todos"):
        """
        Devuelve empleados activos filtrados por búsqueda y departamento.
        La búsqueda compara contra nombre, apellido, puesto y email.
        """
        query  = "SELECT * FROM empleados WHERE activo=1"
        params = []

        if busqueda:
            query += """ AND (
                nombre       LIKE ? OR
                apellido     LIKE ? OR
                puesto       LIKE ? OR
                email        LIKE ? OR
                departamento LIKE ?
            )"""
            like = f"%{busqueda}%"
            params.extend([like, like, like, like, like])

        if departamento != "Todos":
            query += " AND departamento=?"
            params.append(departamento)

        query += " ORDER BY apellido, nombre"
        return self.conn.execute(query, params).fetchall()

    def obtener_por_id(self, emp_id):
        return self.conn.execute(
            "SELECT * FROM empleados WHERE id=?", (emp_id,)
        ).fetchone()

    def insertar(self, datos: dict):
        """Inserta un nuevo empleado. Retorna el ID generado."""
        cursor = self.conn.execute("""
            INSERT INTO empleados
            (nombre, apellido, puesto, departamento, email, telefono, salario, fecha_ingreso, notas)
            VALUES (:nombre, :apellido, :puesto, :departamento, :email, :telefono, :salario, :fecha_ingreso, :notas)
        """, datos)
        self.conn.commit()
        return cursor.lastrowid

    def actualizar(self, emp_id: int, datos: dict):
        """Actualiza todos los campos de un empleado."""
        datos["id"] = emp_id
        self.conn.execute("""
            UPDATE empleados SET
                nombre=:nombre, apellido=:apellido, puesto=:puesto,
                departamento=:departamento, email=:email,
                telefono=:telefono, salario=:salario,
                fecha_ingreso=:fecha_ingreso, notas=:notas
            WHERE id=:id
        """, datos)
        self.conn.commit()

    def eliminar(self, emp_id: int):
        """Soft delete: marca el empleado como inactivo."""
        self.conn.execute(
            "UPDATE empleados SET activo=0 WHERE id=?", (emp_id,)
        )
        self.conn.commit()

    def estadisticas(self):
        """Devuelve estadísticas generales para el dashboard."""
        cur = self.conn.cursor()
        stats = {}

        # Total de empleados activos
        stats["total"] = cur.execute(
            "SELECT COUNT(*) FROM empleados WHERE activo=1"
        ).fetchone()[0]

        # Nómina mensual total
        stats["nomina"] = cur.execute(
            "SELECT COALESCE(SUM(salario),0) FROM empleados WHERE activo=1"
        ).fetchone()[0]

        # Salario promedio
        stats["promedio"] = cur.execute(
            "SELECT COALESCE(AVG(salario),0) FROM empleados WHERE activo=1"
        ).fetchone()[0]

        # Conteo por departamento
        rows = cur.execute("""
            SELECT departamento, COUNT(*) as total
            FROM empleados WHERE activo=1
            GROUP BY departamento
            ORDER BY total DESC
        """).fetchall()
        stats["por_departamento"] = {r["departamento"]: r["total"] for r in rows}

        # Ingreso más reciente
        reciente = cur.execute("""
            SELECT nombre || ' ' || apellido as nombre, fecha_ingreso
            FROM empleados WHERE activo=1
            ORDER BY fecha_ingreso DESC LIMIT 1
        """).fetchone()
        stats["reciente"] = dict(reciente) if reciente else None

        return stats


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  COMPONENTES DE UI REUTILIZABLES                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def make_label(parent, text, size=11, bold=False, color=None, **kwargs):
    """Crea un Label con el estilo del tema oscuro."""
    font   = ("Segoe UI", size, "bold" if bold else "normal")
    color  = color or COLORES["text"]
    return tk.Label(parent, text=text, font=font, fg=color,
                    bg=kwargs.pop("bg", COLORES["bg_panel"]), **kwargs)

def make_entry(parent, textvariable=None, width=30, **kwargs):
    """Campo de texto estilizado."""
    return tk.Entry(
        parent,
        textvariable = textvariable,
        width        = width,
        font         = ("Segoe UI", 10),
        bg           = COLORES["bg_input"],
        fg           = COLORES["text"],
        insertbackground = COLORES["text"],
        relief       = "flat",
        bd           = 0,
        **kwargs
    )

def make_button(parent, text, command, color=None, width=14, **kwargs):
    """Botón estilizado con color de acento."""
    color = color or COLORES["accent"]
    btn = tk.Button(
        parent,
        text             = text,
        command          = command,
        font             = ("Segoe UI", 10, "bold"),
        bg               = color,
        fg               = "white",
        activebackground = color,
        activeforeground = "white",
        relief           = "flat",
        bd               = 0,
        cursor           = "hand2",
        padx             = 12,
        pady             = 6,
        width            = width,
        **kwargs
    )
    # Efecto hover
    btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(color)))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn

def _lighten(hex_color, amount=30):
    """Aclara un color hexadecimal para el efecto hover."""
    hex_color = hex_color.lstrip("#")
    r, g, b   = int(hex_color[0:2],16), int(hex_color[2:4],16), int(hex_color[4:6],16)
    r = min(255, r + amount)
    g = min(255, g + amount)
    b = min(255, b + amount)
    return f"#{r:02x}{g:02x}{b:02x}"

def separador(parent, bg=None):
    """Línea horizontal separadora."""
    tk.Frame(
        parent, height=1,
        bg=bg or COLORES["border"]
    ).pack(fill="x", pady=8)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  VENTANA DE FORMULARIO — Agregar / Editar empleado                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class FormularioEmpleado(tk.Toplevel):
    """
    Ventana modal para agregar o editar un empleado.
    Recibe datos opcionales (edición) o los deja vacíos (nuevo).
    Al guardar llama al callback on_save(datos) del padre.
    """

    def __init__(self, parent, on_save, empleado=None):
        super().__init__(parent)
        self.on_save  = on_save
        self.empleado = empleado
        self.title("Editar empleado" if empleado else "Nuevo empleado")
        self.configure(bg=COLORES["bg_dark"])
        self.resizable(False, False)
        self.grab_set()   # Modal: bloquea la ventana principal mientras está abierta

        self._build_ui()

        # Centrar la ventana en la pantalla
        self.update_idletasks()
        w, h = 520, 620
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Si es edición, prellenar los campos
        if empleado:
            self._prellenar()

    def _build_ui(self):
        """Construye el formulario con todos los campos."""
        # ── Encabezado ──
        header = tk.Frame(self, bg=COLORES["accent"], pady=16)
        header.pack(fill="x")
        icono = "✏️" if self.empleado else "➕"
        make_label(header, f"{icono}  {'Editar' if self.empleado else 'Nuevo'} Empleado",
                   size=14, bold=True, bg=COLORES["accent"]).pack()

        # ── Contenido ──
        body = tk.Frame(self, bg=COLORES["bg_panel"], padx=30, pady=20)
        body.pack(fill="both", expand=True)

        # Variables de los campos
        self.v_nombre   = tk.StringVar()
        self.v_apellido = tk.StringVar()
        self.v_puesto   = tk.StringVar()
        self.v_depto    = tk.StringVar()
        self.v_email    = tk.StringVar()
        self.v_tel      = tk.StringVar()
        self.v_salario  = tk.StringVar()
        self.v_fecha    = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        # Helper para crear fila de campo
        def campo(label, widget_fn, *args, **kwargs):
            make_label(body, label, size=9, color=COLORES["text_dim"],
                       bg=COLORES["bg_panel"]).pack(anchor="w", pady=(10,2))
            w = widget_fn(body, *args, **kwargs)
            w.pack(fill="x", ipady=6)
            return w

        # ── Nombre y Apellido (en fila) ──
        fila1 = tk.Frame(body, bg=COLORES["bg_panel"])
        fila1.pack(fill="x", pady=(10,0))
        col_n = tk.Frame(fila1, bg=COLORES["bg_panel"])
        col_n.pack(side="left", fill="x", expand=True, padx=(0,8))
        col_a = tk.Frame(fila1, bg=COLORES["bg_panel"])
        col_a.pack(side="left", fill="x", expand=True)

        make_label(col_n, "Nombre *", size=9, color=COLORES["text_dim"],
                   bg=COLORES["bg_panel"]).pack(anchor="w", pady=(0,2))
        make_entry(col_n, textvariable=self.v_nombre).pack(fill="x", ipady=6)

        make_label(col_a, "Apellido *", size=9, color=COLORES["text_dim"],
                   bg=COLORES["bg_panel"]).pack(anchor="w", pady=(0,2))
        make_entry(col_a, textvariable=self.v_apellido).pack(fill="x", ipady=6)

        # ── Puesto ──
        make_label(body, "Puesto *", size=9, color=COLORES["text_dim"],
                   bg=COLORES["bg_panel"]).pack(anchor="w", pady=(10,2))
        cb_puesto = ttk.Combobox(body, textvariable=self.v_puesto,
                                  values=PUESTOS, state="readonly",
                                  font=("Segoe UI", 10))
        cb_puesto.pack(fill="x", ipady=4)
        self._style_combobox(cb_puesto)

        # ── Departamento ──
        make_label(body, "Departamento *", size=9, color=COLORES["text_dim"],
                   bg=COLORES["bg_panel"]).pack(anchor="w", pady=(10,2))
        cb_depto = ttk.Combobox(body, textvariable=self.v_depto,
                                  values=DEPARTAMENTOS, state="readonly",
                                  font=("Segoe UI", 10))
        cb_depto.pack(fill="x", ipady=4)
        self._style_combobox(cb_depto)

        # ── Email y Teléfono ──
        fila2 = tk.Frame(body, bg=COLORES["bg_panel"])
        fila2.pack(fill="x", pady=(10,0))
        col_e = tk.Frame(fila2, bg=COLORES["bg_panel"])
        col_e.pack(side="left", fill="x", expand=True, padx=(0,8))
        col_t = tk.Frame(fila2, bg=COLORES["bg_panel"])
        col_t.pack(side="left", fill="x", expand=True)

        make_label(col_e, "Email", size=9, color=COLORES["text_dim"],
                   bg=COLORES["bg_panel"]).pack(anchor="w", pady=(0,2))
        make_entry(col_e, textvariable=self.v_email).pack(fill="x", ipady=6)

        make_label(col_t, "Teléfono", size=9, color=COLORES["text_dim"],
                   bg=COLORES["bg_panel"]).pack(anchor="w", pady=(0,2))
        make_entry(col_t, textvariable=self.v_tel).pack(fill="x", ipady=6)

        # ── Salario y Fecha ──
        fila3 = tk.Frame(body, bg=COLORES["bg_panel"])
        fila3.pack(fill="x", pady=(10,0))
        col_s = tk.Frame(fila3, bg=COLORES["bg_panel"])
        col_s.pack(side="left", fill="x", expand=True, padx=(0,8))
        col_f = tk.Frame(fila3, bg=COLORES["bg_panel"])
        col_f.pack(side="left", fill="x", expand=True)

        make_label(col_s, "Salario mensual ($) *", size=9, color=COLORES["text_dim"],
                   bg=COLORES["bg_panel"]).pack(anchor="w", pady=(0,2))
        make_entry(col_s, textvariable=self.v_salario).pack(fill="x", ipady=6)

        make_label(col_f, "Fecha ingreso (YYYY-MM-DD) *", size=9,
                   color=COLORES["text_dim"], bg=COLORES["bg_panel"]).pack(anchor="w", pady=(0,2))
        make_entry(col_f, textvariable=self.v_fecha).pack(fill="x", ipady=6)

        # ── Notas ──
        make_label(body, "Notas", size=9, color=COLORES["text_dim"],
                   bg=COLORES["bg_panel"]).pack(anchor="w", pady=(10,2))
        self.txt_notas = tk.Text(
            body, height=3, font=("Segoe UI", 10),
            bg=COLORES["bg_input"], fg=COLORES["text"],
            insertbackground=COLORES["text"], relief="flat", bd=0
        )
        self.txt_notas.pack(fill="x", ipady=4)

        # ── Botones ──
        separador(body)
        btn_frame = tk.Frame(body, bg=COLORES["bg_panel"])
        btn_frame.pack(fill="x")
        make_button(btn_frame, "Cancelar", self.destroy,
                    color=COLORES["border"], width=12).pack(side="left")
        make_button(btn_frame, "💾 Guardar", self._guardar,
                    color=COLORES["accent"], width=14).pack(side="right")

    def _style_combobox(self, cb):
        """Aplica estilos al widget Combobox (limitado en tkinter)."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                         fieldbackground = COLORES["bg_input"],
                         background      = COLORES["bg_input"],
                         foreground      = COLORES["text"],
                         selectbackground= COLORES["accent"],
                         borderwidth     = 0)

    def _prellenar(self):
        """Rellena los campos con los datos del empleado a editar."""
        e = self.empleado
        self.v_nombre.set(e["nombre"])
        self.v_apellido.set(e["apellido"])
        self.v_puesto.set(e["puesto"])
        self.v_depto.set(e["departamento"])
        self.v_email.set(e["email"] or "")
        self.v_tel.set(e["telefono"] or "")
        self.v_salario.set(str(e["salario"]))
        self.v_fecha.set(e["fecha_ingreso"])
        if e["notas"]:
            self.txt_notas.insert("1.0", e["notas"])

    def _guardar(self):
        """Valida los campos y llama al callback on_save."""
        # Validación de campos obligatorios
        errores = []
        if not self.v_nombre.get().strip():   errores.append("Nombre")
        if not self.v_apellido.get().strip(): errores.append("Apellido")
        if not self.v_puesto.get():           errores.append("Puesto")
        if not self.v_depto.get():            errores.append("Departamento")
        if not self.v_fecha.get().strip():    errores.append("Fecha de ingreso")

        try:
            salario = float(self.v_salario.get().replace(",", ""))
            if salario < 0:
                raise ValueError
        except ValueError:
            errores.append("Salario (debe ser un número positivo)")

        if errores:
            messagebox.showerror(
                "Campos incompletos",
                "Por favor completa los siguientes campos:\n• " + "\n• ".join(errores),
                parent=self
            )
            return

        datos = {
            "nombre":       self.v_nombre.get().strip().title(),
            "apellido":     self.v_apellido.get().strip().title(),
            "puesto":       self.v_puesto.get(),
            "departamento": self.v_depto.get(),
            "email":        self.v_email.get().strip() or None,
            "telefono":     self.v_tel.get().strip() or None,
            "salario":      salario,
            "fecha_ingreso":self.v_fecha.get().strip(),
            "notas":        self.txt_notas.get("1.0", "end-1c") or None,
        }

        self.on_save(datos)
        self.destroy()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  VENTANA PRINCIPAL — Sistema RRHH                                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class AppRRHH(tk.Tk):
    """
    Ventana principal del sistema.
    Organiza la UI en:
      - Sidebar izquierdo (navegación: Empleados / Dashboard)
      - Área principal derecha (cambia según la sección)
    """

    def __init__(self):
        super().__init__()
        self.title("Sistema RRHH — Abraham Ramos")
        self.configure(bg=COLORES["bg_dark"])
        self.resizable(True, True)

        # Centrar y dimensionar la ventana
        w, h = 1100, 680
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(900, 580)

        self.db            = Database()
        self.seccion_actual = "empleados"
        self.emp_selec_id  = None   # ID del empleado seleccionado en la tabla

        self._build_ui()
        self._cargar_empleados()

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _build_ui(self):
        """Divide la ventana en sidebar + área principal."""
        # ── Sidebar ──
        self.sidebar = tk.Frame(self, bg=COLORES["bg_panel"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # ── Área principal ──
        self.main_area = tk.Frame(self, bg=COLORES["bg_dark"])
        self.main_area.pack(side="left", fill="both", expand=True)
        self._build_empleados_section()

    def _build_sidebar(self):
        """Sidebar con logo y botones de navegación."""
        # Logo
        logo_frame = tk.Frame(self.sidebar, bg=COLORES["accent"], pady=20)
        logo_frame.pack(fill="x")
        make_label(logo_frame, "👥", size=28, bg=COLORES["accent"]).pack()
        make_label(logo_frame, "RRHH Sistema", size=11, bold=True,
                   bg=COLORES["accent"]).pack()

        # Separador
        tk.Frame(self.sidebar, height=1, bg=COLORES["border"]).pack(fill="x", pady=10)

        # Botones de navegación
        nav_items = [
            ("👨‍💼  Empleados",  "empleados"),
            ("📊  Dashboard",   "dashboard"),
        ]
        self.nav_btns = {}
        for label, key in nav_items:
            btn = tk.Button(
                self.sidebar, text=label,
                command=lambda k=key: self._navegar(k),
                font=("Segoe UI", 11),
                bg=COLORES["bg_panel"], fg=COLORES["text"],
                activebackground=COLORES["bg_card"],
                activeforeground=COLORES["text"],
                relief="flat", bd=0, cursor="hand2",
                anchor="w", padx=20, pady=12, width=20
            )
            btn.pack(fill="x")
            self.nav_btns[key] = btn

        self._highlight_nav("empleados")

        # Info en la parte inferior
        tk.Frame(self.sidebar, bg=COLORES["border"], height=1).pack(
            side="bottom", fill="x")
        info = tk.Frame(self.sidebar, bg=COLORES["bg_panel"], pady=12)
        info.pack(side="bottom", fill="x")
        make_label(info, "Abraham Ramos", size=9, bold=True,
                   bg=COLORES["bg_panel"]).pack()
        make_label(info, "github.com/abrahamramoskd", size=8,
                   color=COLORES["text_dim"], bg=COLORES["bg_panel"]).pack()

    def _highlight_nav(self, key):
        """Resalta el botón de navegación activo."""
        for k, btn in self.nav_btns.items():
            if k == key:
                btn.config(bg=COLORES["accent"], fg="white")
            else:
                btn.config(bg=COLORES["bg_panel"], fg=COLORES["text"])

    def _navegar(self, seccion):
        """Cambia la sección visible en el área principal."""
        if self.seccion_actual == seccion:
            return
        self.seccion_actual = seccion
        self._highlight_nav(seccion)

        # Limpiar área principal
        for w in self.main_area.winfo_children():
            w.destroy()

        if seccion == "empleados":
            self._build_empleados_section()
            self._cargar_empleados()
        elif seccion == "dashboard":
            self._build_dashboard_section()

    # ── SECCIÓN: EMPLEADOS ────────────────────────────────────────────────────

    def _build_empleados_section(self):
        """Construye la vista de lista de empleados."""

        # ── Encabezado ──
        header = tk.Frame(self.main_area, bg=COLORES["bg_panel"], pady=16, padx=24)
        header.pack(fill="x")

        make_label(header, "👨‍💼 Gestión de Empleados", size=16, bold=True,
                   bg=COLORES["bg_panel"]).pack(side="left")

        make_button(header, "➕ Nuevo empleado", self._nuevo_empleado,
                    color=COLORES["accent"]).pack(side="right")

        tk.Frame(self.main_area, bg=COLORES["border"], height=1).pack(fill="x")

        # ── Barra de búsqueda y filtros ──
        barra = tk.Frame(self.main_area, bg=COLORES["bg_dark"], pady=12, padx=16)
        barra.pack(fill="x")

        # Campo de búsqueda
        make_label(barra, "🔍", size=13, bg=COLORES["bg_dark"]).pack(side="left", padx=(0,6))
        self.v_busqueda = tk.StringVar()
        self.v_busqueda.trace("w", lambda *_: self._cargar_empleados())
        entry_busq = make_entry(barra, textvariable=self.v_busqueda, width=35)
        entry_busq.pack(side="left", ipady=6, padx=(0,16))
        entry_busq.insert(0, "")

        # Placeholder simulado
        entry_busq.bind("<FocusIn>",  lambda e: None)
        entry_busq.bind("<FocusOut>", lambda e: None)

        # Filtro por departamento
        make_label(barra, "Depto:", size=10, bg=COLORES["bg_dark"],
                   color=COLORES["text_dim"]).pack(side="left", padx=(0,6))
        self.v_filtro_depto = tk.StringVar(value="Todos")
        self.v_filtro_depto.trace("w", lambda *_: self._cargar_empleados())
        cb_filtro = ttk.Combobox(
            barra, textvariable=self.v_filtro_depto,
            values=["Todos"] + DEPARTAMENTOS,
            state="readonly", width=14, font=("Segoe UI", 10)
        )
        cb_filtro.pack(side="left")

        # Contador de resultados
        self.lbl_count = make_label(barra, "", size=9, color=COLORES["text_dim"],
                                     bg=COLORES["bg_dark"])
        self.lbl_count.pack(side="right", padx=8)

        # ── Tabla de empleados ──
        tabla_frame = tk.Frame(self.main_area, bg=COLORES["bg_dark"], padx=16, pady=8)
        tabla_frame.pack(fill="both", expand=True)

        # Columnas de la tabla
        cols = ("ID", "Nombre", "Puesto", "Departamento", "Email", "Salario", "Ingreso")
        self.tabla = ttk.Treeview(
            tabla_frame, columns=cols, show="headings",
            selectmode="browse", height=18
        )

        # Estilo de la tabla
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background      = COLORES["bg_panel"],
                         foreground      = COLORES["text"],
                         fieldbackground = COLORES["bg_panel"],
                         rowheight       = 34,
                         font            = ("Segoe UI", 10))
        style.configure("Treeview.Heading",
                         background  = COLORES["bg_card"],
                         foreground  = COLORES["text"],
                         font        = ("Segoe UI", 10, "bold"),
                         relief      = "flat")
        style.map("Treeview",
                   background=[("selected", COLORES["accent"])],
                   foreground=[("selected", "white")])

        # Definir columnas
        anchos = {"ID":45, "Nombre":160, "Puesto":130, "Departamento":120,
                  "Email":180, "Salario":100, "Ingreso":100}
        for col in cols:
            self.tabla.heading(col, text=col,
                               command=lambda c=col: self._ordenar(c))
            self.tabla.column(col, width=anchos.get(col, 100),
                              anchor="center" if col in ("ID","Salario","Ingreso") else "w")

        # Scrollbar vertical
        scroll = ttk.Scrollbar(tabla_frame, orient="vertical",
                               command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Evento de selección
        self.tabla.bind("<<TreeviewSelect>>", self._on_select)
        self.tabla.bind("<Double-1>",          self._editar_empleado)

        # ── Panel de acciones (aparece al seleccionar) ──
        self.panel_acciones = tk.Frame(self.main_area, bg=COLORES["bg_panel"], pady=10, padx=16)
        self.panel_acciones.pack(fill="x")
        self.lbl_selec = make_label(
            self.panel_acciones, "Selecciona un empleado para ver opciones",
            size=10, color=COLORES["text_dim"], bg=COLORES["bg_panel"]
        )
        self.lbl_selec.pack(side="left")

        self.btn_editar = make_button(
            self.panel_acciones, "✏️ Editar", self._editar_empleado,
            color=COLORES["warning"], width=10
        )
        self.btn_eliminar = make_button(
            self.panel_acciones, "🗑️ Eliminar", self._eliminar_empleado,
            color=COLORES["danger"], width=10
        )
        self.btn_exportar = make_button(
            self.panel_acciones, "📄 Exportar", self._exportar,
            color=COLORES["accent2"], width=10
        )
        self.btn_exportar.pack(side="right", padx=4)
        self.btn_eliminar.pack(side="right", padx=4)
        self.btn_editar.pack(side="right", padx=4)

    def _cargar_empleados(self):
        """Carga (o recarga) la lista de empleados en la tabla."""
        busqueda = self.v_busqueda.get() if hasattr(self, "v_busqueda") else ""
        depto    = self.v_filtro_depto.get() if hasattr(self, "v_filtro_depto") else "Todos"

        # Limpiar la tabla
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        empleados = self.db.obtener_todos(busqueda, depto)

        # Insertar filas con colores alternados
        for i, emp in enumerate(empleados):
            tag  = "par" if i % 2 == 0 else "impar"
            # Tag especial por departamento para colorear
            d_tag = emp["departamento"].replace(" ", "_")

            self.tabla.insert("", "end", iid=str(emp["id"]), tags=(tag, d_tag),
                values=(
                    emp["id"],
                    f"{emp['nombre']} {emp['apellido']}",
                    emp["puesto"],
                    emp["departamento"],
                    emp["email"] or "—",
                    f"${emp['salario']:,.0f}",
                    emp["fecha_ingreso"],
                ))

        # Colores de filas
        self.tabla.tag_configure("par",   background=COLORES["bg_panel"])
        self.tabla.tag_configure("impar", background=COLORES["row_alt"])

        # Actualizar contador
        n = len(empleados)
        if hasattr(self, "lbl_count"):
            self.lbl_count.config(
                text=f"{n} empleado{'s' if n != 1 else ''} encontrado{'s' if n != 1 else ''}"
            )

        self.emp_selec_id = None

    def _on_select(self, event):
        """Al seleccionar una fila, muestra el nombre en el panel de acciones."""
        sel = self.tabla.selection()
        if sel:
            self.emp_selec_id = int(sel[0])
            emp = self.db.obtener_por_id(self.emp_selec_id)
            self.lbl_selec.config(
                text=f"✅ Seleccionado: {emp['nombre']} {emp['apellido']} — {emp['puesto']}",
                fg=COLORES["text"]
            )

    def _ordenar(self, col):
        """Ordena la tabla al hacer clic en el encabezado de columna."""
        # Obtener todos los datos actuales
        data = [(self.tabla.set(c, col), c) for c in self.tabla.get_children("")]
        try:
            data.sort(key=lambda x: float(x[0].replace("$","").replace(",","")))
        except ValueError:
            data.sort()
        for i, (_, iid) in enumerate(data):
            self.tabla.move(iid, "", i)

    # ── CRUD desde la UI ──────────────────────────────────────────────────────

    def _nuevo_empleado(self):
        """Abre el formulario para crear un nuevo empleado."""
        def guardar(datos):
            self.db.insertar(datos)
            self._cargar_empleados()
            messagebox.showinfo("✅ Éxito", "Empleado registrado correctamente.")
        FormularioEmpleado(self, on_save=guardar)

    def _editar_empleado(self, event=None):
        """Abre el formulario precargado para editar el empleado seleccionado."""
        if not self.emp_selec_id:
            messagebox.showwarning("Sin selección", "Selecciona un empleado primero.")
            return
        emp = self.db.obtener_por_id(self.emp_selec_id)

        def guardar(datos):
            self.db.actualizar(self.emp_selec_id, datos)
            self._cargar_empleados()
            messagebox.showinfo("✅ Éxito", "Empleado actualizado correctamente.")

        FormularioEmpleado(self, on_save=guardar, empleado=emp)

    def _eliminar_empleado(self):
        """Solicita confirmación y elimina (soft delete) el empleado."""
        if not self.emp_selec_id:
            messagebox.showwarning("Sin selección", "Selecciona un empleado primero.")
            return
        emp = self.db.obtener_por_id(self.emp_selec_id)
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Deseas eliminar a {emp['nombre']} {emp['apellido']}?\n"
            "Esta acción no se puede deshacer.",
        )
        if confirmar:
            self.db.eliminar(self.emp_selec_id)
            self.emp_selec_id = None
            self.lbl_selec.config(
                text="Selecciona un empleado para ver opciones",
                fg=COLORES["text_dim"]
            )
            self._cargar_empleados()

    def _exportar(self):
        """Exporta la lista de empleados a un archivo .txt."""
        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt")],
            initialfile=f"reporte_empleados_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        if not ruta:
            return

        empleados = self.db.obtener_todos(
            self.v_busqueda.get(),
            self.v_filtro_depto.get()
        )
        stats = self.db.estadisticas()

        lineas = [
            "=" * 70,
            "  REPORTE DE EMPLEADOS — SISTEMA RRHH",
            f"  Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"  Autor: Abraham Ramos | github.com/abrahamramoskd",
            "=" * 70,
            "",
            f"  Total de empleados: {stats['total']}",
            f"  Nómina mensual:     ${stats['nomina']:,.2f}",
            f"  Salario promedio:   ${stats['promedio']:,.2f}",
            "",
            "-" * 70,
            f"  {'ID':<5} {'Nombre':<25} {'Puesto':<18} {'Depto':<14} {'Salario':>10}",
            "-" * 70,
        ]
        for emp in empleados:
            nombre = f"{emp['nombre']} {emp['apellido']}"
            lineas.append(
                f"  {emp['id']:<5} {nombre:<25} {emp['puesto']:<18} "
                f"{emp['departamento']:<14} ${emp['salario']:>9,.0f}"
            )

        lineas += ["", "=" * 70]

        with open(ruta, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas))

        messagebox.showinfo("✅ Exportado", f"Reporte guardado en:\n{ruta}")

    # ── SECCIÓN: DASHBOARD ────────────────────────────────────────────────────

    def _build_dashboard_section(self):
        """Construye el panel de estadísticas y métricas."""
        stats = self.db.estadisticas()

        # ── Encabezado ──
        header = tk.Frame(self.main_area, bg=COLORES["bg_panel"], pady=16, padx=24)
        header.pack(fill="x")
        make_label(header, "📊 Dashboard — Estadísticas", size=16, bold=True,
                   bg=COLORES["bg_panel"]).pack(side="left")

        tk.Frame(self.main_area, bg=COLORES["border"], height=1).pack(fill="x")

        scroll_frame = tk.Frame(self.main_area, bg=COLORES["bg_dark"])
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=16)

        # ── Tarjetas de KPIs ──
        kpi_frame = tk.Frame(scroll_frame, bg=COLORES["bg_dark"])
        kpi_frame.pack(fill="x", pady=(0,20))

        kpis = [
            ("👥 Empleados", str(stats["total"]), "activos", COLORES["accent"]),
            ("💰 Nómina",    f"${stats['nomina']:,.0f}", "mensual", COLORES["success"]),
            ("📈 Promedio",  f"${stats['promedio']:,.0f}", "por empleado", COLORES["warning"]),
            ("🏢 Deptos",   str(len(stats["por_departamento"])), "con personal", COLORES["accent2"]),
        ]

        for i, (titulo, valor, subtitulo, color) in enumerate(kpis):
            card = tk.Frame(kpi_frame, bg=COLORES["bg_card"],
                            padx=20, pady=16, relief="flat")
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            kpi_frame.columnconfigure(i, weight=1)

            # Barra de color en la parte superior de la tarjeta
            tk.Frame(card, bg=color, height=4).pack(fill="x", pady=(0,10))
            make_label(card, titulo, size=10, color=COLORES["text_dim"],
                       bg=COLORES["bg_card"]).pack()
            make_label(card, valor, size=22, bold=True, color=color,
                       bg=COLORES["bg_card"]).pack(pady=4)
            make_label(card, subtitulo, size=9, color=COLORES["text_dim"],
                       bg=COLORES["bg_card"]).pack()

        separador(scroll_frame)

        # ── Distribución por departamento ──
        make_label(scroll_frame, "Distribución por Departamento",
                   size=13, bold=True, bg=COLORES["bg_dark"]).pack(anchor="w", pady=(0,12))

        dept_frame = tk.Frame(scroll_frame, bg=COLORES["bg_dark"])
        dept_frame.pack(fill="x")

        total = stats["total"] or 1
        for depto, count in sorted(stats["por_departamento"].items(),
                                    key=lambda x: -x[1]):
            pct   = count / total
            color = DEPT_COLORS.get(depto, COLORES["text_dim"])

            fila = tk.Frame(dept_frame, bg=COLORES["bg_dark"])
            fila.pack(fill="x", pady=4)

            # Nombre del departamento
            make_label(fila, depto, size=10, color=color,
                       bg=COLORES["bg_dark"], width=16, anchor="w").pack(side="left")

            # Barra de progreso manual (canvas)
            bar_bg = tk.Frame(fila, bg=COLORES["border"], height=16, width=320)
            bar_bg.pack(side="left", padx=8)
            bar_bg.pack_propagate(False)
            bar_fill = tk.Frame(bar_bg, bg=color, height=16,
                                width=int(320 * pct))
            bar_fill.place(x=0, y=0, relheight=1)

            make_label(fila, f"{count} emp. ({pct*100:.0f}%)",
                       size=9, color=COLORES["text_dim"],
                       bg=COLORES["bg_dark"]).pack(side="left", padx=8)

        separador(scroll_frame)

        # ── Último ingreso ──
        if stats["reciente"]:
            rec = stats["reciente"]
            make_label(scroll_frame, "🆕 Último ingreso",
                       size=11, bold=True, bg=COLORES["bg_dark"]).pack(anchor="w")
            make_label(scroll_frame,
                       f"{rec['nombre']}  —  {rec['fecha_ingreso']}",
                       size=10, color=COLORES["accent2"],
                       bg=COLORES["bg_dark"]).pack(anchor="w", pady=4)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  PUNTO DE ENTRADA                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    app = AppRRHH()
    app.mainloop()
