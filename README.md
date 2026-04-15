# 👥 Sistema RRHH — Gestión de Empleados

![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=flat-square&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-built--in-4b8bbe?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-local-003b57?style=flat-square&logo=sqlite&logoColor=white)
![Sin dependencias](https://img.shields.io/badge/dependencias-ninguna-2ed573?style=flat-square)
![License](https://img.shields.io/badge/licencia-MIT-6e9ef0?style=flat-square)

Sistema de gestión de empleados con interfaz gráfica moderna en tema oscuro. Registro, búsqueda, edición y estadísticas — todo guardado en una base de datos SQLite local. Sin instalaciones extra.

## 🖥️ Preview

> Interfaz oscura profesional con sidebar de navegación, tabla interactiva de empleados y dashboard con KPIs y barras de progreso por departamento.

## 🚀 Cómo ejecutar

```bash
python rrhh.py
```

> Tkinter viene incluido con Python. No requiere instalar ningún paquete adicional.

**Requisitos:**
- Python 3.8 o superior
- Sistema operativo: Windows, macOS o Linux

## ✅ Funcionalidades

### 👨‍💼 Gestión de Empleados
- Registro completo: nombre, apellido, puesto, departamento, email, teléfono, salario, fecha de ingreso y notas
- Búsqueda en tiempo real por nombre, apellido, puesto, email o departamento
- Filtro por departamento desde un selector desplegable
- Edición de empleados con formulario modal precargado
- Eliminación con soft delete (no borra el registro, lo desactiva)
- Ordenamiento por columna al hacer clic en el encabezado
- Doble clic en una fila para editar rápidamente

### 📊 Dashboard
- Total de empleados activos
- Nómina mensual total
- Salario promedio
- Número de departamentos con personal
- Distribución visual por departamento con barras de progreso y colores únicos
- Último empleado registrado

### 📄 Exportación
- Exporta el listado actual a un archivo `.txt` con resumen de estadísticas incluido
- El nombre del archivo incluye la fecha de generación automáticamente

## 🗂️ Departamentos disponibles

`Tecnología` · `Ventas` · `Finanzas` · `RRHH` · `Operaciones` · `Marketing` · `Legal` · `Otro`

Cada departamento tiene su propio color en la tabla y en el dashboard.

## 🛠️ Tecnologías

- **Python** — lógica principal y base de datos
- **Tkinter + ttk** — interfaz gráfica nativa
- **SQLite** — base de datos local (archivo `rrhh.db`, se crea automáticamente)

## 📁 Estructura

```
rrhh-dashboard/
├── rrhh.py       ← Aplicación completa (UI + DB + lógica)
└── rrhh.db       ← Base de datos SQLite (se genera al ejecutar)
```

## 🧱 Arquitectura del código

| Clase / Función | Responsabilidad |
|---|---|
| `Database` | Toda la interacción con SQLite (CRUD + estadísticas) |
| `FormularioEmpleado` | Ventana modal para agregar o editar empleados |
| `AppRRHH` | Ventana principal: sidebar, tabla, dashboard y acciones |
| `make_label / make_entry / make_button` | Componentes de UI reutilizables con el tema oscuro |

## 🎨 Tema visual

Paleta oscura profesional con acento en morado (`#6c63ff`) y verde-cian (`#00d4aa`). Los colores de departamento se aplican tanto en la tabla como en las barras del dashboard para una lectura visual inmediata.

## 📄 Licencia

MIT — úsalo en lo que quieras, personal o comercial.

---

Hecho con ❤️ por [abrahamramoskd](https://github.com/abrahamramoskd)  
Si te fue útil, dale una ⭐ al repo!
