import sqlite3
import hashlib
import hmac
import os
import html
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple

import streamlit as st

# =============================
# CONFIGURACIÓN GENERAL
# =============================
APP_TITLE = "ROL DE TURNOS - PERSONAL DE SALUD"
APP_SUBTITLE = "BANCO DE SANGRE DE TARIJA"
DB_PATH = os.environ.get("ROL_SALUD_DB", "rol_salud.db")

PROFESSIONS = [
    "Médicos",
    "Enfermeras",
    "Bioquímicos / Biotecnólogos",
]

SHIFTS = [
    ("Mañana", "☀️", "#FFF4C2", "#7A4F00"),
    ("Tarde", "🌤️", "#FFD7A8", "#7A3200"),
    ("Noche", "🌙", "#CFE2FF", "#123C69"),
]

DEFAULT_SHIFT_HOURS = {
    "Mañana": ("07:00", "13:00"),
    "Tarde": ("13:00", "19:00"),
    "Noche": ("19:00", "07:00"),
}

DEFAULT_USERS = [
    ("personal", "personal123", "user", "Personal / Jefaturas"),
    ("admin", "admin123", "admin", "Administrador"),
]

# =============================
# ESTILOS MÓVILES
# =============================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 3.2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1200px;
    }
    .main-title {
        font-size: clamp(1.65rem, 6vw, 3.1rem);
        font-weight: 900;
        line-height: 1.18;
        color: #0f172a;
        text-align: center;
        margin-top: .8rem;
        margin-bottom: .35rem;
        padding-top: .45rem;
        overflow: visible;
    }
    .subtitle {
        font-size: clamp(1.15rem, 4vw, 1.7rem);
        color: #b91c1c;
        text-align: center;
        margin-bottom: 1.1rem;
        font-weight: 900;
        letter-spacing: .04em;
    }
    .login-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 24px;
        padding: 1.2rem;
        box-shadow: 0 12px 28px rgba(15, 23, 42, .08);
    }
    .day-banner {
        border-radius: 22px;
        padding: 1rem 1.2rem;
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 12px 28px rgba(15, 23, 42, .16);
    }
    .day-banner h2 {
        margin: 0;
        font-size: clamp(1.35rem, 5vw, 2.3rem);
        color: white;
    }
    .day-banner p {
        margin: .2rem 0 0 0;
        font-size: clamp(.95rem, 3vw, 1.15rem);
        color: #dbeafe;
    }
    .profession-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 26px;
        padding: 1rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 25px rgba(15, 23, 42, .07);
    }
    .profession-title {
        font-size: clamp(1.4rem, 5vw, 2.2rem);
        font-weight: 900;
        color: #111827;
        margin-bottom: .8rem;
        text-align: center;
    }
    .shift-card {
        border-radius: 23px;
        padding: 1rem;
        min-height: 210px;
        border: 2px solid rgba(15, 23, 42, .08);
        margin-bottom: .8rem;
    }
    .shift-title {
        font-size: clamp(1.35rem, 5vw, 2.1rem);
        font-weight: 900;
        margin-bottom: .25rem;
        display: flex;
        align-items: center;
        gap: .5rem;
    }
    .shift-hours {
        display: inline-block;
        background: rgba(255,255,255,.72);
        border: 1px solid rgba(15, 23, 42, .12);
        border-radius: 999px;
        padding: .35rem .65rem;
        margin-bottom: .6rem;
        font-size: clamp(1rem, 3.8vw, 1.35rem);
        font-weight: 900;
        letter-spacing: .01em;
    }
    .staff-pill {
        background: rgba(255,255,255,.72);
        border: 1px solid rgba(15, 23, 42, .10);
        border-radius: 18px;
        padding: .65rem .75rem;
        margin: .45rem 0;
        font-size: clamp(1.1rem, 4.2vw, 1.55rem);
        font-weight: 800;
        line-height: 1.2;
    }
    .empty-pill {
        background: rgba(255,255,255,.45);
        border: 1px dashed rgba(15, 23, 42, .25);
        border-radius: 18px;
        padding: .75rem;
        font-size: clamp(1rem, 3.8vw, 1.3rem);
        font-weight: 700;
        opacity: .75;
    }
    .message-box {
        border-radius: 24px;
        padding: 1rem 1.1rem;
        background: #ecfeff;
        border: 2px solid #06b6d4;
        color: #164e63;
        font-size: clamp(1.15rem, 4.3vw, 1.65rem);
        font-weight: 850;
        line-height: 1.25;
        box-shadow: 0 10px 24px rgba(8, 145, 178, .16);
        margin-top: 1.2rem;
        margin-bottom: 1.4rem;
    }
    .small-note {
        color: #64748b;
        font-size: .95rem;
    }
    div[data-testid="stButton"] button {
        border-radius: 14px;
        font-weight: 800;
        min-height: 44px;
    }
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div, div[data-testid="stDateInput"] input {
        border-radius: 13px;
    }
    @media (max-width: 768px) {
        .block-container { padding-top: 3.8rem; padding-left: .75rem; padding-right: .75rem; }
        .main-title { font-size: clamp(1.45rem, 7vw, 2.35rem); line-height: 1.25; }
        .subtitle { font-size: clamp(1rem, 4.4vw, 1.35rem); }
        .shift-card { min-height: auto; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================
# BASE DE DATOS
# =============================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','user')),
            display_name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            profession TEXT NOT NULL,
            phone TEXT,
            notes TEXT,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shift_date TEXT NOT NULL,
            profession TEXT NOT NULL,
            shift TEXT NOT NULL,
            staff_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(shift_date, profession, shift, staff_id),
            FOREIGN KEY(staff_id) REFERENCES staff(id) ON DELETE CASCADE
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            detail TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    now = datetime.now().isoformat(timespec="seconds")
    for username, password, role, display_name in DEFAULT_USERS:
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO users(username, password_hash, role, display_name, created_at) VALUES(?,?,?,?,?)",
                (username, hash_password(password), role, display_name, now),
            )

    defaults = {
        "public_message": "",
        "public_message_active": "0",
    }
    for shift_name, (start_time, end_time) in DEFAULT_SHIFT_HOURS.items():
        defaults[f"shift_{shift_name}_start"] = start_time
        defaults[f"shift_{shift_name}_end"] = end_time
    for key, value in defaults.items():
        cur.execute("INSERT OR IGNORE INTO settings(key, value) VALUES(?,?)", (key, value))

    conn.commit()
    conn.close()


def log_action(action: str, detail: str) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO audit_log(action, detail, created_at) VALUES(?,?,?)",
        (action, detail, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def authenticate(username: str, password: str) -> Optional[sqlite3.Row]:
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
    conn.close()
    if user and verify_password(password, user["password_hash"]):
        return user
    return None


def get_setting(key: str, default: str = "") -> str:
    conn = get_conn()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO settings(key, value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    conn.commit()
    conn.close()


def get_shift_hours(shift: str) -> Tuple[str, str]:
    default_start, default_end = DEFAULT_SHIFT_HOURS.get(shift, ("", ""))
    start = get_setting(f"shift_{shift}_start", default_start)
    end = get_setting(f"shift_{shift}_end", default_end)
    return start, end


def set_shift_hours(shift: str, start_time: str, end_time: str) -> None:
    set_setting(f"shift_{shift}_start", start_time)
    set_setting(f"shift_{shift}_end", end_time)
    log_action("HORARIO_TURNO", f"Se actualizó {shift}: {start_time} a {end_time}")


def list_staff(active_only: bool = False, profession: Optional[str] = None) -> List[sqlite3.Row]:
    conn = get_conn()
    query = "SELECT * FROM staff WHERE 1=1"
    params: List = []
    if active_only:
        query += " AND active = 1"
    if profession:
        query += " AND profession = ?"
        params.append(profession)
    query += " ORDER BY profession, active DESC, full_name COLLATE NOCASE"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_staff(staff_id: int) -> Optional[sqlite3.Row]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM staff WHERE id = ?", (staff_id,)).fetchone()
    conn.close()
    return row


def add_staff(full_name: str, profession: str, phone: str, notes: str) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_conn()
    conn.execute(
        "INSERT INTO staff(full_name, profession, phone, notes, active, created_at, updated_at) VALUES(?,?,?,?,1,?,?)",
        (full_name.strip(), profession, phone.strip(), notes.strip(), now, now),
    )
    conn.commit()
    conn.close()
    log_action("ALTA_PERSONAL", f"Se agregó personal: {full_name} - {profession}")


def update_staff(staff_id: int, full_name: str, profession: str, phone: str, notes: str, active: bool) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_conn()
    conn.execute(
        "UPDATE staff SET full_name=?, profession=?, phone=?, notes=?, active=?, updated_at=? WHERE id=?",
        (full_name.strip(), profession, phone.strip(), notes.strip(), 1 if active else 0, now, staff_id),
    )
    conn.commit()
    conn.close()
    log_action("EDITAR_PERSONAL", f"Se editó personal ID {staff_id}: {full_name}")


def delete_staff(staff_id: int) -> None:
    staff = get_staff(staff_id)
    conn = get_conn()
    conn.execute("DELETE FROM assignments WHERE staff_id = ?", (staff_id,))
    conn.execute("DELETE FROM staff WHERE id = ?", (staff_id,))
    conn.commit()
    conn.close()
    log_action("ELIMINAR_PERSONAL", f"Se eliminó personal ID {staff_id}: {staff['full_name'] if staff else ''}")


def get_assignments(shift_date: str, profession: Optional[str] = None, shift: Optional[str] = None) -> List[sqlite3.Row]:
    conn = get_conn()
    query = """
        SELECT a.id, a.shift_date, a.profession, a.shift, s.id AS staff_id, s.full_name, s.phone, s.active
        FROM assignments a
        JOIN staff s ON s.id = a.staff_id
        WHERE a.shift_date = ?
    """
    params: List = [shift_date]
    if profession:
        query += " AND a.profession = ?"
        params.append(profession)
    if shift:
        query += " AND a.shift = ?"
        params.append(shift)
    query += " ORDER BY a.profession, a.shift, s.full_name COLLATE NOCASE"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def selected_staff_ids(shift_date: str, profession: str, shift: str) -> List[int]:
    rows = get_assignments(shift_date, profession, shift)
    return [int(row["staff_id"]) for row in rows]


def save_assignment(shift_date: str, profession: str, shift: str, staff_ids: List[int]) -> Tuple[bool, str]:
    if len(staff_ids) > 5:
        return False, "Solo se permiten hasta 5 profesionales por profesión y turno."

    conn = get_conn()
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        "DELETE FROM assignments WHERE shift_date = ? AND profession = ? AND shift = ?",
        (shift_date, profession, shift),
    )
    for staff_id in staff_ids:
        conn.execute(
            "INSERT OR IGNORE INTO assignments(shift_date, profession, shift, staff_id, created_at) VALUES(?,?,?,?,?)",
            (shift_date, profession, shift, int(staff_id), now),
        )
    conn.commit()
    conn.close()
    log_action("GUARDAR_ROL", f"{shift_date} | {profession} | {shift} | {len(staff_ids)} asignados")
    return True, "Rol guardado correctamente."


def clear_day(shift_date: str) -> None:
    conn = get_conn()
    conn.execute("DELETE FROM assignments WHERE shift_date = ?", (shift_date,))
    conn.commit()
    conn.close()
    log_action("LIMPIAR_DIA", f"Se limpió el rol del día {shift_date}")


def update_password(username: str, new_password: str) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (hash_password(new_password), username),
    )
    conn.commit()
    conn.close()
    log_action("CAMBIO_CLAVE", f"Se cambió la contraseña del usuario {username}")


def get_users() -> List[sqlite3.Row]:
    conn = get_conn()
    rows = conn.execute("SELECT id, username, role, display_name, created_at FROM users ORDER BY role, username").fetchall()
    conn.close()
    return rows

# =============================
# UTILIDADES DE PANTALLA
# =============================
def format_date(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def date_to_db(d: date) -> str:
    return d.isoformat()


def html_escape(value: str) -> str:
    return html.escape(value or "")


def render_header() -> None:
    st.markdown(f"<div class='main-title'>🏥 {APP_TITLE}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>{APP_SUBTITLE}</div>", unsafe_allow_html=True)


def logout_button(label: str = "Salir") -> None:
    if st.button(label, use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.rerun()


def render_roster(selected_date: date) -> None:
    db_date = date_to_db(selected_date)
    st.markdown(
        f"""
        <div class='day-banner'>
            <h2>Rol del día: {format_date(selected_date)}</h2>
            <p>Vista para personal y jefaturas</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    assignments = get_assignments(db_date)
    by_key: Dict[Tuple[str, str], List[str]] = {}
    for row in assignments:
        by_key.setdefault((row["profession"], row["shift"]), []).append(row["full_name"])

    for profession in PROFESSIONS:
        st.markdown("<div class='profession-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='profession-title'>{html_escape(profession)}</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, (shift, icon, bg, fg) in enumerate(SHIFTS):
            names = by_key.get((profession, shift), [])
            start_time, end_time = get_shift_hours(shift)
            with cols[idx]:
                people_html = ""
                if names:
                    for name in names:
                        people_html += f"<div class='staff-pill'>👤 {html_escape(name)}</div>"
                else:
                    people_html = "<div class='empty-pill'>Sin personal asignado</div>"
                st.markdown(
                    f"""
                    <div class='shift-card' style='background:{bg}; color:{fg};'>
                        <div class='shift-title'>{icon} {html_escape(shift)}</div>
                        <div class='shift-hours'>🕒 {html_escape(start_time)} a {html_escape(end_time)}</div>
                        {people_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    public_message = get_setting("public_message", "")
    active = get_setting("public_message_active", "0") == "1"
    if active and public_message.strip():
        st.markdown(
            f"<div class='message-box'>📢 {html_escape(public_message).replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True,
        )


def login_screen() -> None:
    render_header()
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.subheader("Ingreso al sistema")
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar", use_container_width=True)
    if submitted:
        user = authenticate(username, password)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = user["username"]
            st.session_state["role"] = user["role"]
            st.session_state["display_name"] = user["display_name"]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

    st.markdown("</div>", unsafe_allow_html=True)


def sidebar_session() -> None:
    with st.sidebar:
        st.markdown(f"### Sesión")
        st.write(f"**Usuario:** {st.session_state.get('display_name','')}")
        st.write(f"**Rol:** {'Administrador' if st.session_state.get('role') == 'admin' else 'Solo lectura'}")
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.clear()
            st.rerun()


def user_view() -> None:
    render_header()
    logout_button("Salir")
    sidebar_session()
    selected_date = st.date_input("Seleccionar fecha", value=date.today(), format="DD/MM/YYYY")
    render_roster(selected_date)


def admin_view() -> None:
    render_header()
    logout_button("Salir")
    sidebar_session()
    st.success("Modo administrador: puede cargar roles, personal y mensaje visible.")

    tab_rol, tab_personal, tab_horarios, tab_mensaje, tab_seguridad, tab_exportar = st.tabs(
        ["📅 Cargar roles", "👥 Personal", "⏰ Horarios", "📢 Mensaje inferior", "🔐 Usuarios", "📦 Respaldo"]
    )

    with tab_rol:
        st.subheader("Cargar rol por fecha")
        selected_date = st.date_input("Fecha del rol", value=date.today(), format="DD/MM/YYYY", key="admin_date")
        db_date = date_to_db(selected_date)
        st.markdown("<span class='small-note'>Seleccione hasta 5 personas por profesión y turno.</span>", unsafe_allow_html=True)

        for profession in PROFESSIONS:
            with st.expander(f"{profession}", expanded=True):
                active_staff = list_staff(active_only=True, profession=profession)
                options = {f"{row['full_name']}" + (f" - {row['phone']}" if row['phone'] else ""): int(row["id"]) for row in active_staff}
                labels_by_id = {v: k for k, v in options.items()}

                if not active_staff:
                    st.warning(f"No hay personal activo registrado para {profession}.")
                    continue

                cols = st.columns(3)
                for idx, (shift, icon, bg, fg) in enumerate(SHIFTS):
                    with cols[idx]:
                        current_ids = selected_staff_ids(db_date, profession, shift)
                        default_labels = [labels_by_id[i] for i in current_ids if i in labels_by_id]
                        selection = st.multiselect(
                            f"{icon} {shift}",
                            options=list(options.keys()),
                            default=default_labels,
                            max_selections=5,
                            key=f"sel_{db_date}_{profession}_{shift}",
                            help="Máximo 5 profesionales.",
                        )
                        if st.button(f"Guardar {shift}", key=f"save_{db_date}_{profession}_{shift}", use_container_width=True):
                            ids = [options[label] for label in selection]
                            ok, msg = save_assignment(db_date, profession, shift, ids)
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Ver rol de esta fecha", use_container_width=True):
                st.session_state["preview_date"] = selected_date
        with c2:
            if st.button("Limpiar todo el rol de esta fecha", use_container_width=True, type="secondary"):
                clear_day(db_date)
                st.warning("Se eliminaron las asignaciones de esta fecha.")
                st.rerun()

        if st.session_state.get("preview_date"):
            st.subheader("Vista previa")
            render_roster(st.session_state["preview_date"])

    with tab_personal:
        st.subheader("Altas de personal")
        with st.form("add_staff_form", clear_on_submit=True):
            full_name = st.text_input("Nombre completo")
            profession = st.selectbox("Profesión", PROFESSIONS)
            phone = st.text_input("Teléfono / referencia", placeholder="Opcional")
            notes = st.text_area("Observaciones", placeholder="Opcional")
            submitted = st.form_submit_button("Agregar personal", use_container_width=True)
        if submitted:
            if not full_name.strip():
                st.error("Debe colocar el nombre completo.")
            else:
                add_staff(full_name, profession, phone, notes)
                st.success("Personal agregado correctamente.")
                st.rerun()

        st.divider()
        st.subheader("Editar, dar baja o eliminar")
        staff_rows = list_staff(active_only=False)
        if not staff_rows:
            st.info("Aún no hay personal registrado.")
        else:
            staff_options = {
                f"{row['full_name']} | {row['profession']} | {'Activo' if row['active'] else 'Baja'}": int(row["id"])
                for row in staff_rows
            }
            selected_label = st.selectbox("Seleccione personal", list(staff_options.keys()))
            selected_id = staff_options[selected_label]
            row = get_staff(selected_id)
            if row:
                with st.form("edit_staff_form"):
                    e_name = st.text_input("Nombre completo", value=row["full_name"])
                    e_profession = st.selectbox("Profesión", PROFESSIONS, index=PROFESSIONS.index(row["profession"]) if row["profession"] in PROFESSIONS else 0)
                    e_phone = st.text_input("Teléfono / referencia", value=row["phone"] or "")
                    e_notes = st.text_area("Observaciones", value=row["notes"] or "")
                    e_active = st.checkbox("Activo", value=bool(row["active"]))
                    update_btn = st.form_submit_button("Guardar cambios", use_container_width=True)
                if update_btn:
                    if not e_name.strip():
                        st.error("Debe colocar el nombre completo.")
                    else:
                        update_staff(selected_id, e_name, e_profession, e_phone, e_notes, e_active)
                        st.success("Cambios guardados.")
                        st.rerun()

                st.warning("Eliminar borra también sus asignaciones de turnos. Para una baja normal, quite el check 'Activo' y guarde cambios.")
                confirm_delete = st.checkbox("Confirmo que deseo eliminar definitivamente a esta persona", key="confirm_delete_staff")
                if st.button("Eliminar definitivamente", disabled=not confirm_delete, use_container_width=True):
                    delete_staff(selected_id)
                    st.success("Personal eliminado.")
                    st.rerun()

    with tab_horarios:
        st.subheader("Horarios visibles por cada turno")
        st.info("Estos horarios aparecerán en letras grandes dentro de cada turno, tanto para personal como para jefaturas.")

        with st.form("shift_hours_form"):
            new_hours = {}
            for shift, icon, bg, fg in SHIFTS:
                current_start, current_end = get_shift_hours(shift)
                st.markdown(f"### {icon} {shift}")
                c1, c2 = st.columns(2)
                with c1:
                    start_value = st.text_input(
                        f"Hora de inicio - {shift}",
                        value=current_start,
                        key=f"start_{shift}",
                        placeholder="Ejemplo: 07:00",
                    )
                with c2:
                    end_value = st.text_input(
                        f"Hora de salida - {shift}",
                        value=current_end,
                        key=f"end_{shift}",
                        placeholder="Ejemplo: 13:00",
                    )
                new_hours[shift] = (start_value.strip(), end_value.strip())

            save_hours = st.form_submit_button("Guardar horarios", use_container_width=True)

        if save_hours:
            incomplete = [shift for shift, (start, end) in new_hours.items() if not start or not end]
            if incomplete:
                st.error("Debe colocar hora de inicio y hora de salida en todos los turnos.")
            else:
                for shift, (start, end) in new_hours.items():
                    set_shift_hours(shift, start, end)
                st.success("Horarios actualizados correctamente.")
                st.rerun()

        st.divider()
        st.subheader("Vista previa de horarios")
        cols = st.columns(3)
        for idx, (shift, icon, bg, fg) in enumerate(SHIFTS):
            start_time, end_time = get_shift_hours(shift)
            with cols[idx]:
                st.markdown(
                    f"""
                    <div class='shift-card' style='background:{bg}; color:{fg}; min-height:auto;'>
                        <div class='shift-title'>{icon} {html_escape(shift)}</div>
                        <div class='shift-hours'>🕒 {html_escape(start_time)} a {html_escape(end_time)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab_mensaje:
        st.subheader("Mensaje inferior visible para personal y jefaturas")
        current_message = get_setting("public_message", "")
        current_active = get_setting("public_message_active", "0") == "1"
        with st.form("message_form"):
            msg = st.text_area(
                "Mensaje que aparecerá abajo del rol",
                value=current_message,
                height=160,
                placeholder="Ejemplo: Presentarse 15 minutos antes del turno. Uso obligatorio de credencial.",
            )
            active_msg = st.checkbox("Mostrar mensaje al personal", value=current_active)
            save_msg = st.form_submit_button("Guardar mensaje", use_container_width=True)
        if save_msg:
            set_setting("public_message", msg.strip())
            set_setting("public_message_active", "1" if active_msg else "0")
            log_action("MENSAJE_PUBLICO", "Se actualizó el mensaje inferior visible")
            st.success("Mensaje actualizado.")
            st.rerun()
        st.info("Cuando el check esté activado, el mensaje se verá al final de la pantalla del rol diario.")

    with tab_seguridad:
        st.subheader("Usuarios del sistema")
        users = get_users()
        for u in users:
            st.write(f"**{u['display_name']}** — usuario: `{u['username']}` — rol: `{u['role']}`")

        st.divider()
        st.subheader("Cambiar contraseñas")
        with st.form("password_form"):
            user_to_change = st.selectbox("Usuario", [u["username"] for u in users])
            new_pass = st.text_input("Nueva contraseña", type="password")
            new_pass2 = st.text_input("Repetir nueva contraseña", type="password")
            save_pass = st.form_submit_button("Cambiar contraseña", use_container_width=True)
        if save_pass:
            if len(new_pass) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            elif new_pass != new_pass2:
                st.error("Las contraseñas no coinciden.")
            else:
                update_password(user_to_change, new_pass)
                st.success("Contraseña actualizada correctamente.")

    with tab_exportar:
        st.subheader("Respaldo rápido")
        st.write("Puede descargar la base SQLite para tener una copia de seguridad.")
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "rb") as f:
                st.download_button(
                    "Descargar base de datos",
                    data=f.read(),
                    file_name=f"rol_salud_backup_{date.today().isoformat()}.db",
                    mime="application/octet-stream",
                    use_container_width=True,
                )
        st.caption("En Streamlit Cloud, si vuelve a desplegar desde cero, conviene guardar respaldos periódicos.")

# =============================
# INICIO
# =============================
init_db()

if not st.session_state.get("logged_in"):
    login_screen()
else:
    if st.session_state.get("role") == "admin":
        admin_view()
    else:
        user_view()
