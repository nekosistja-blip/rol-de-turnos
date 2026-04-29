# ROL DE TURNOS - PERSONAL DE SALUD

**BANCO DE SANGRE DE TARIJA**

Aplicación móvil en línea creada con **Streamlit + SQLite** para cargar y visualizar roles de personal de salud por fecha, profesión, turno y horario individual por persona.

## Accesos iniciales

### Personal / Jefaturas
- Usuario: `personal`
- Contraseña: `personal123`

### Administrador
- Usuario: `admin`
- Contraseña: `admin123`

> La pantalla de ingreso no muestra usuarios ni contraseñas. Se recomienda cambiar las contraseñas desde el panel de administrador después del primer ingreso.

## Funciones principales

- Vista móvil con letras grandes y colores por turno.
- Título: **ROL DE TURNOS - PERSONAL DE SALUD**.
- Subtítulo: **BANCO DE SANGRE DE TARIJA**.
- Botón **Salir** visible para personal y administrador.
- Tres turnos: **Mañana, Tarde y Noche**.
- Tres grupos profesionales:
  - Médicos
  - Enfermeras
  - Bioquímicos / Biotecnólogos
- Máximo **5 profesionales por profesión y turno**.
- Usuario de solo lectura para personal y jefaturas.
- Administrador para:
  - Agregar personal.
  - Editar personal.
  - Dar bajas.
  - Eliminar registros.
  - Cargar roles por fecha.
  - Colocar hora de entrada y salida individual para cada persona.
  - Activar/desactivar mensaje inferior visible.
  - Cambiar contraseñas.
  - Descargar respaldo de base de datos.

## Horarios individuales por persona

En esta versión, el horario ya no es solamente general por turno. El administrador puede marcar a cada persona y escribir su horario individual.

Ejemplo:

- Turno Tarde
- Dra. Jaqueline
- Entrada: `12:00`
- Salida: `16:00`

En la vista del personal se mostrará así:

**Dra. Jaqueline**  
**12:00 a 16:00**

## Instalación local

1. Instalar Python 3.11 o superior.
2. Abrir terminal en esta carpeta.
3. Ejecutar:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en GitHub + Streamlit Cloud

1. Crear un repositorio nuevo en GitHub.
2. Subir estos archivos:
   - `app.py`
   - `requirements.txt`
   - carpeta `.streamlit`
   - `README.md`
3. Entrar a Streamlit Community Cloud.
4. Crear una app nueva.
5. Elegir el repositorio de GitHub.
6. En archivo principal colocar:

```text
app.py
```

7. Deploy.
8. Compartir el enlace generado con el personal y jefaturas.

## Nota sobre la base de datos

La app crea automáticamente el archivo `rol_salud.db` la primera vez que se ejecuta.

Si ya tenía una versión anterior, esta versión agrega automáticamente las columnas de horario individual sin borrar los datos existentes.

En Streamlit Cloud, SQLite funciona para una implementación simple, pero se recomienda descargar respaldos desde el panel de administrador. Para un sistema institucional con datos permanentes y muchos usuarios, se recomienda migrar la base a PostgreSQL, Supabase o similar.
