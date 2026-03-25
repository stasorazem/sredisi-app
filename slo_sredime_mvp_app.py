import sqlite3
from datetime import datetime, date, timedelta

import pandas as pd
import streamlit as st

DB_PATH = "uredime_v4.db"


# -------------------------
# DATABASE
# -------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def execute(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


def fetch_all(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_one(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS salons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            category TEXT NOT NULL,
            address TEXT,
            description TEXT,
            rating REAL DEFAULT 0,
            image_url TEXT,
            active INTEGER DEFAULT 1
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            salon_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            FOREIGN KEY (salon_id) REFERENCES salons (id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            salon_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            duration_min INTEGER NOT NULL,
            price_eur REAL NOT NULL,
            category TEXT,
            FOREIGN KEY (salon_id) REFERENCES salons (id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            salon_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'rezervirano',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (salon_id) REFERENCES salons (id),
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (service_id) REFERENCES services (id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            salon_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            stars INTEGER NOT NULL,
            comment TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (salon_id) REFERENCES salons (id)
        )
        """
    )

    conn.commit()

    cur.execute("SELECT COUNT(*) as cnt FROM salons")
    if cur.fetchone()["cnt"] == 0:
        seed_data(conn)

    conn.close()


def seed_data(conn):
    cur = conn.cursor()

    salons = [
        ("Studio Lepota Koper", "Koper", "Frizerstvo", "Pristaniška 12, Koper", "Striženje, barvanje in nega las.", 4.8, "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f"),
        ("Koper Beauty Room", "Koper", "Kozmetika", "Ferrarska 8, Koper", "Nega obraza, obrvi in trepalnice.", 4.7, "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f"),

        ("Morski SPA Izola", "Izola", "SPA", "Veliki trg 4, Izola", "Masaže in sprostitveni tretmaji.", 4.6, "https://images.unsplash.com/photo-1515377905703-c4788e51af15"),
        ("Izola Nail Studio", "Izola", "Nail", "Cankarjev drevored 3, Izola", "Manikira in pedikira.", 4.5, "https://images.unsplash.com/photo-1604654894610-df63bc536371"),

        ("Portorož Beauty Center", "Portorož", "SPA", "Obala 33, Portorož", "Wellness in premium SPA storitve.", 4.9, "https://images.unsplash.com/photo-1500840216050-6ffa99d75160"),
        ("Portorož Hair Lounge", "Portorož", "Frizerstvo", "Obala 21, Portorož", "Moderne ženske in moške frizure.", 4.6, "https://images.unsplash.com/photo-1560066984-138dadb4c035"),

        ("Ljubljana Glow Bar", "Ljubljana", "Beauty", "Trubarjeva 22, Ljubljana", "Moderen beauty salon.", 4.9, "https://images.unsplash.com/photo-1604654894610-df63bc536371"),
        ("Frizerski Studio Šiška", "Ljubljana", "Frizerstvo", "Celovška 88, Ljubljana", "Hitra in kvalitetna frizura.", 4.5, "https://images.unsplash.com/photo-1560066984-138dadb4c035"),
        ("Ljubljana Zen SPA", "Ljubljana", "SPA", "Dunajska 55, Ljubljana", "Masaže, savna in wellness paketi.", 4.8, "https://images.unsplash.com/photo-1519823551278-64ac92734fb1"),

        ("Maribor Style Studio", "Maribor", "Frizerstvo", "Glavni trg 5, Maribor", "Trend frizure in barvanje.", 4.7, "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e"),
        ("Maribor Beauty Point", "Maribor", "Kozmetika", "Partizanska 14, Maribor", "Nega kože in makeup.", 4.6, "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f"),

        ("Celje Beauty Point", "Celje", "Kozmetika", "Center 12, Celje", "Nega obraza in telesa.", 4.6, "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f"),
        ("Celje Hair Studio", "Celje", "Frizerstvo", "Stanetova 7, Celje", "Barvanje, styling in striženje.", 4.5, "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"),

        ("Kranj Hair Lounge", "Kranj", "Frizerstvo", "Prešernova 10, Kranj", "Premium hair styling.", 4.8, "https://images.unsplash.com/photo-1524504388940-b1c1722653e1"),
        ("Kranj Relax Center", "Kranj", "SPA", "Gregorčičeva 9, Kranj", "Masaže in sprostitveni programi.", 4.5, "https://images.unsplash.com/photo-1519823551278-64ac92734fb1"),

        ("Novo mesto Wellness", "Novo mesto", "SPA", "Glavni trg 2, Novo mesto", "Sprostitveni programi.", 4.5, "https://images.unsplash.com/photo-1519823551278-64ac92734fb1"),
        ("Novo mesto Beauty Lab", "Novo mesto", "Beauty", "Rozmanova 11, Novo mesto", "Ličenje, obrvi in lash lift.", 4.4, "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f"),

        ("Nova Gorica Shine", "Nova Gorica", "Beauty", "Kidričeva 5, Nova Gorica", "Beauty tretmaji in nega obraza.", 4.6, "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f"),
        ("Nova Gorica Hair & Spa", "Nova Gorica", "SPA", "Delpinova 4, Nova Gorica", "Wellness in nega las.", 4.5, "https://images.unsplash.com/photo-1515377905703-c4788e51af15"),
    ]

    cur.executemany(
        """
        INSERT INTO salons (name, city, category, address, description, rating, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        salons,
    )

    cur.execute("SELECT id, name FROM salons")
    salon_map = {row["name"]: row["id"] for row in cur.fetchall()}

    employees = [
        (salon_map["Studio Lepota Koper"], "Nina", "Frizerka"),
        (salon_map["Koper Beauty Room"], "Sara", "Kozmetičarka"),

        (salon_map["Morski SPA Izola"], "Marko", "Maser"),
        (salon_map["Izola Nail Studio"], "Tjaša", "Nail artist"),

        (salon_map["Portorož Beauty Center"], "Eva", "SPA terapevtka"),
        (salon_map["Portorož Hair Lounge"], "David", "Frizer"),

        (salon_map["Ljubljana Glow Bar"], "Ana", "Beauty specialist"),
        (salon_map["Frizerski Studio Šiška"], "Miha", "Frizer"),
        (salon_map["Ljubljana Zen SPA"], "Petra", "Wellness terapevtka"),

        (salon_map["Maribor Style Studio"], "Luka", "Frizer"),
        (salon_map["Maribor Beauty Point"], "Maja", "Kozmetičarka"),

        (salon_map["Celje Beauty Point"], "Nika", "Kozmetičarka"),
        (salon_map["Celje Hair Studio"], "Rok", "Frizer"),

        (salon_map["Kranj Hair Lounge"], "Tanja", "Frizerka"),
        (salon_map["Kranj Relax Center"], "Blaž", "Maser"),

        (salon_map["Novo mesto Wellness"], "Katja", "Maserka"),
        (salon_map["Novo mesto Beauty Lab"], "Lara", "Makeup artist"),

        (salon_map["Nova Gorica Shine"], "Eva", "Beauty specialist"),
        (salon_map["Nova Gorica Hair & Spa"], "Alen", "Wellness specialist"),
    ]
    cur.executemany(
        "INSERT INTO employees (salon_id, name, role) VALUES (?, ?, ?)",
        employees,
    )

    services = [
        (salon_map["Studio Lepota Koper"], "Žensko striženje", 60, 32, "Frizerstvo"),
        (salon_map["Studio Lepota Koper"], "Barvanje las", 120, 58, "Frizerstvo"),
        (salon_map["Koper Beauty Room"], "Nega obraza", 60, 42, "Kozmetika"),
        (salon_map["Koper Beauty Room"], "Lash lift", 45, 35, "Kozmetika"),

        (salon_map["Morski SPA Izola"], "Klasična masaža", 60, 50, "SPA"),
        (salon_map["Morski SPA Izola"], "Wellness paket", 90, 80, "SPA"),
        (salon_map["Izola Nail Studio"], "Gel manikira", 60, 34, "Nail"),
        (salon_map["Izola Nail Studio"], "Pedikira", 50, 32, "Nail"),

        (salon_map["Portorož Beauty Center"], "Luxury SPA", 90, 100, "SPA"),
        (salon_map["Portorož Beauty Center"], "Aroma masaža", 60, 70, "SPA"),
        (salon_map["Portorož Hair Lounge"], "Moško striženje", 35, 22, "Frizerstvo"),
        (salon_map["Portorož Hair Lounge"], "Styling", 45, 30, "Frizerstvo"),

        (salon_map["Ljubljana Glow Bar"], "Manikira", 60, 35, "Beauty"),
        (salon_map["Ljubljana Glow Bar"], "Lash lift", 45, 39, "Beauty"),
        (salon_map["Frizerski Studio Šiška"], "Moško striženje", 30, 20, "Frizerstvo"),
        (salon_map["Frizerski Studio Šiška"], "Barvanje", 120, 60, "Frizerstvo"),
        (salon_map["Ljubljana Zen SPA"], "Masaža hrbta", 45, 40, "SPA"),
        (salon_map["Ljubljana Zen SPA"], "Antistres paket", 90, 85, "SPA"),

        (salon_map["Maribor Style Studio"], "Barvanje las", 120, 55, "Frizerstvo"),
        (salon_map["Maribor Style Studio"], "Styling", 45, 28, "Frizerstvo"),
        (salon_map["Maribor Beauty Point"], "Nega kože", 60, 40, "Kozmetika"),
        (salon_map["Maribor Beauty Point"], "Oblikovanje obrvi", 25, 18, "Kozmetika"),

        (salon_map["Celje Beauty Point"], "Nega obraza", 60, 41, "Kozmetika"),
        (salon_map["Celje Beauty Point"], "Ličenje", 50, 38, "Kozmetika"),
        (salon_map["Celje Hair Studio"], "Striženje", 45, 24, "Frizerstvo"),
        (salon_map["Celje Hair Studio"], "Fen frizura", 30, 18, "Frizerstvo"),

        (salon_map["Kranj Hair Lounge"], "Styling", 45, 35, "Frizerstvo"),
        (salon_map["Kranj Hair Lounge"], "Barvanje", 110, 57, "Frizerstvo"),
        (salon_map["Kranj Relax Center"], "Sprostitvena masaža", 60, 46, "SPA"),
        (salon_map["Kranj Relax Center"], "SPA paket", 90, 82, "SPA"),

        (salon_map["Novo mesto Wellness"], "Masaža", 60, 45, "SPA"),
        (salon_map["Novo mesto Wellness"], "Wellness paket", 90, 78, "SPA"),
        (salon_map["Novo mesto Beauty Lab"], "Makeup", 50, 37, "Beauty"),
        (salon_map["Novo mesto Beauty Lab"], "Lash lift", 45, 34, "Beauty"),

        (salon_map["Nova Gorica Shine"], "Nega obraza", 60, 43, "Beauty"),
        (salon_map["Nova Gorica Shine"], "Obrvi in trepalnice", 40, 29, "Beauty"),
        (salon_map["Nova Gorica Hair & Spa"], "Masaža", 60, 47, "SPA"),
        (salon_map["Nova Gorica Hair & Spa"], "Nega las", 50, 33, "SPA"),
    ]
    cur.executemany(
        """
        INSERT INTO services (salon_id, name, duration_min, price_eur, category)
        VALUES (?, ?, ?, ?, ?)
        """,
        services,
    )

    reviews = [
        (salon_map["Studio Lepota Koper"], "Petra", 5, "Zelo prijazni in točni.", datetime.now().isoformat()),
        (salon_map["Morski SPA Izola"], "Matej", 4, "Odlična masaža in lep ambient.", datetime.now().isoformat()),
        (salon_map["Ljubljana Glow Bar"], "Nika", 5, "Top nohti, zelo priporočam.", datetime.now().isoformat()),
    ]
    cur.executemany(
        """
        INSERT INTO reviews (salon_id, customer_name, stars, comment, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        reviews,
    )

    conn.commit()


# -------------------------
# AUTH
# -------------------------
def register_user(full_name, email, password):
    existing = fetch_one("SELECT * FROM users WHERE email = ?", (email,))
    if existing:
        return False, "Ta e-pošta že obstaja."

    execute(
        """
        INSERT INTO users (full_name, email, password, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (full_name, email, password, datetime.now().isoformat()),
    )
    return True, "Registracija uspešna."


def login_user(email, password):
    return fetch_one(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, password),
    )


# -------------------------
# HELPERS
# -------------------------
def get_salons(city=None, category=None, search=None):
    query = "SELECT * FROM salons WHERE active = 1"
    params = []

    if city and city != "Vsa mesta":
        query += " AND city = ?"
        params.append(city)

    if category and category != "Vse kategorije":
        query += " AND category = ?"
        params.append(category)

    if search and search.strip():
        query += " AND (name LIKE ? OR description LIKE ? OR address LIKE ?)"
        like = f"%{search.strip()}%"
        params.extend([like, like, like])

    query += " ORDER BY city ASC, rating DESC, name ASC"
    return fetch_all(query, tuple(params))


def get_employees(salon_id):
    return fetch_all(
        "SELECT * FROM employees WHERE salon_id = ? ORDER BY name ASC",
        (salon_id,),
    )


def get_services(salon_id):
    return fetch_all(
        "SELECT * FROM services WHERE salon_id = ? ORDER BY category, name ASC",
        (salon_id,),
    )


def get_reviews(salon_id):
    return fetch_all(
        "SELECT * FROM reviews WHERE salon_id = ? ORDER BY id DESC",
        (salon_id,),
    )


def get_available_times(employee_id, booking_date, service_duration=60):
    start_hour = 8
    end_hour = 19
    slots = []

    current = datetime.combine(booking_date, datetime.min.time()).replace(hour=start_hour, minute=0)
    end_dt = datetime.combine(booking_date, datetime.min.time()).replace(hour=end_hour, minute=0)

    existing = fetch_all(
        """
        SELECT b.booking_time, s.duration_min
        FROM bookings b
        JOIN services s ON b.service_id = s.id
        WHERE b.employee_id = ?
          AND b.booking_date = ?
          AND b.status IN ('rezervirano', 'potrjeno')
        """,
        (employee_id, booking_date.isoformat()),
    )

    occupied = []
    for row in existing:
        booked_start = datetime.combine(
            booking_date,
            datetime.strptime(row["booking_time"], "%H:%M").time()
        )
        booked_end = booked_start + timedelta(minutes=row["duration_min"])
        occupied.append((booked_start, booked_end))

    while current + timedelta(minutes=service_duration) <= end_dt:
        proposed_end = current + timedelta(minutes=service_duration)
        conflict = any(
            current < occ_end and proposed_end > occ_start
            for occ_start, occ_end in occupied
        )
        if not conflict:
            slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=30)

    return slots


def create_booking(user_id, salon_id, employee_id, service_id, booking_date, booking_time):
    return execute(
        """
        INSERT INTO bookings (
            user_id, salon_id, employee_id, service_id,
            booking_date, booking_time, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'rezervirano', ?)
        """,
        (
            user_id,
            salon_id,
            employee_id,
            service_id,
            booking_date.isoformat(),
            booking_time,
            datetime.now().isoformat(),
        ),
    )


def get_user_bookings(user_id):
    return fetch_all(
        """
        SELECT
            b.id,
            s.name AS salon_name,
            s.city,
            e.name AS employee_name,
            sv.name AS service_name,
            sv.price_eur,
            b.booking_date,
            b.booking_time,
            b.status
        FROM bookings b
        JOIN salons s ON s.id = b.salon_id
        JOIN employees e ON e.id = b.employee_id
        JOIN services sv ON sv.id = b.service_id
        WHERE b.user_id = ?
        ORDER BY b.booking_date DESC, b.booking_time DESC
        """,
        (user_id,),
    )


def add_review(salon_id, customer_name, stars, comment):
    execute(
        """
        INSERT INTO reviews (salon_id, customer_name, stars, comment, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (salon_id, customer_name, stars, comment, datetime.now().isoformat()),
    )


# -------------------------
# UI STYLE
# -------------------------
def setup_page():
    st.set_page_config(page_title="UrediMe", page_icon="✨", layout="wide")

    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(180deg, #fff7fb 0%, #ffffff 55%, #fffaf3 100%);
            }
            .block-container {
                padding-top: 1.8rem;
                padding-bottom: 2rem;
                max-width: 1380px;
            }
            .hero-box {
                background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
                color: white;
                padding: 2rem;
                border-radius: 26px;
                box-shadow: 0 18px 50px rgba(17,24,39,0.18);
                margin-bottom: 1rem;
            }
            .hero-badge {
                display: inline-block;
                background: rgba(255,255,255,0.12);
                padding: 0.35rem 0.75rem;
                border-radius: 999px;
                font-size: 0.82rem;
                font-weight: 700;
                margin-bottom: 0.8rem;
            }
            .hero-title {
                font-size: 3rem;
                font-weight: 800;
                margin: 0;
                line-height: 1;
            }
            .hero-title span {
                color: #f9a8d4;
            }
            .hero-text {
                margin-top: 0.8rem;
                color: #e5e7eb;
                font-size: 1.02rem;
                max-width: 760px;
            }
            .small-card {
                background: white;
                border: 1px solid #f1f5f9;
                border-radius: 20px;
                padding: 1rem;
                box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
                margin-bottom: 1rem;
            }
            .ad-box {
                background: linear-gradient(135deg, #fdf2f8 0%, #fff7ed 100%);
                border: 1px solid #fbcfe8;
                border-radius: 22px;
                padding: 1rem;
                box-shadow: 0 12px 28px rgba(236, 72, 153, 0.08);
            }
            .ad-title {
                font-size: 1.2rem;
                font-weight: 800;
                margin-bottom: 0.4rem;
            }
            .ad-badge {
                display: inline-block;
                padding: 0.25rem 0.55rem;
                background: #ec4899;
                color: white;
                border-radius: 999px;
                font-size: 0.72rem;
                font-weight: 700;
                margin-bottom: 0.6rem;
            }
            .profile-box {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 22px;
                padding: 1rem;
                box-shadow: 0 10px 30px rgba(15,23,42,0.05);
            }
            div[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #fff7fb 0%, #ffffff 100%);
                border-right: 1px solid #f3e8ff;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
        <div class="hero-box">
            <div class="hero-badge">✨ Slovenska platforma za rezervacije</div>
            <h1 class="hero-title">Uredi<span>Me</span></h1>
            <div class="hero-text">
                Rezerviraj salon, spremljaj svoje termine, prijavi se v profil in odkrij najboljše beauty in wellness storitve po Sloveniji.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_ad():
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div class="ad-box">
            <div class="ad-badge">OGLAS</div>
            <div class="ad-title">-20% na premium nego obraza</div>
            <div style="font-size:0.92rem; color:#374151; margin-bottom:0.7rem;">
                Samo ta teden v salonu Glow Bar Ljubljana. Rezerviraj zdaj in prejmi welcome paket.
            </div>
            <div style="font-size:0.82rem; color:#6b7280;">
                Fake promocijski prostor za oglaševanje partnerjev.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------
# AUTH UI
# -------------------------
def auth_view():
    st.title("Prijava / Registracija")

    tab1, tab2 = st.tabs(["Prijava", "Registracija"])

    with tab1:
        email = st.text_input("E-pošta", key="login_email")
        password = st.text_input("Geslo", type="password", key="login_password")

        if st.button("Prijavi se", type="primary"):
            user = login_user(email.strip(), password.strip())
            if user:
                st.session_state["user"] = user
                st.success("Uspešna prijava.")
                st.rerun()
            else:
                st.error("Napačen email ali geslo.")

    with tab2:
        full_name = st.text_input("Ime in priimek", key="reg_name")
        email = st.text_input("E-pošta", key="reg_email")
        password = st.text_input("Geslo", type="password", key="reg_password")

        if st.button("Ustvari račun"):
            if not full_name.strip() or not email.strip() or not password.strip():
                st.warning("Izpolni vsa polja.")
            else:
                ok, msg = register_user(full_name.strip(), email.strip(), password.strip())
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


# -------------------------
# MAIN PAGES
# -------------------------
def salon_card(salon):
    with st.container(border=True):
        col1, col2 = st.columns([1.1, 2])
        with col1:
            if salon.get("image_url"):
                st.image(salon["image_url"], use_container_width=True)
        with col2:
            st.subheader(salon["name"])
            st.write(f"**Mesto:** {salon['city']}")
            st.write(f"**Kategorija:** {salon['category']}")
            st.write(f"**Ocena:** ⭐ {salon['rating']}")
            st.write(f"**Naslov:** {salon.get('address', '')}")
            st.write(salon.get("description", ""))


def bookings_page():
    render_header()

    cities = ["Vsa mesta"] + [
        r["city"] for r in fetch_all("SELECT DISTINCT city FROM salons ORDER BY city")
    ]
    categories = ["Vse kategorije"] + [
        r["category"] for r in fetch_all("SELECT DISTINCT category FROM salons ORDER BY category")
    ]

    left, right = st.columns([3.3, 1.2])

    with left:
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            city = st.selectbox("Mesto", cities)
        with col2:
            category = st.selectbox("Kategorija", categories)
        with col3:
            search = st.text_input("Išči salon, opis ali naslov")

        salons = get_salons(city=city, category=category, search=search)

        if not salons:
            st.warning("Ni zadetkov za izbrane filtre.")
            return

        salon_labels = [f"{s['name']} ({s['city']}) ⭐ {s['rating']}" for s in salons]
        selected_label = st.selectbox("Izberi salon", salon_labels)
        selected = salons[salon_labels.index(selected_label)]

        salon_card(selected)

        tab1, tab2, tab3 = st.tabs(["Rezervacija", "Storitve in zaposleni", "Ocene"])

        with tab1:
            st.markdown("### Rezerviraj termin")
            employees = get_employees(selected["id"])
            services = get_services(selected["id"])

            if not employees or not services:
                st.info("Ta salon še nima dodanih zaposlenih ali storitev.")
            else:
                employee_labels = [f"{e['name']} — {e['role']}" for e in employees]
                service_labels = [
                    f"{s['name']} ({s['duration_min']} min / {s['price_eur']:.2f} €)"
                    for s in services
                ]

                c1, c2 = st.columns(2)
                with c1:
                    chosen_employee_label = st.selectbox("Izberi zaposlenega", employee_labels)
                with c2:
                    chosen_service_label = st.selectbox("Izberi storitev", service_labels)

                chosen_employee = employees[employee_labels.index(chosen_employee_label)]
                chosen_service = services[service_labels.index(chosen_service_label)]

                min_date = date.today()
                max_date = date.today() + timedelta(days=30)
                chosen_date = st.date_input(
                    "Datum",
                    min_value=min_date,
                    max_value=max_date,
                    value=min_date,
                )

                available_times = get_available_times(
                    chosen_employee["id"],
                    chosen_date,
                    chosen_service["duration_min"],
                )

                if available_times:
                    chosen_time = st.selectbox("Prosti termini", available_times)
                else:
                    chosen_time = None
                    st.error("Za izbran datum ni prostih terminov.")

                if st.button("Potrdi rezervacijo", type="primary", disabled=chosen_time is None):
                    booking_id = create_booking(
                        st.session_state["user"]["id"],
                        selected["id"],
                        chosen_employee["id"],
                        chosen_service["id"],
                        chosen_date,
                        chosen_time,
                    )
                    st.success(f"Rezervacija uspešna. ID: #{booking_id}")
                    st.info(
                        f"{selected['name']} • {chosen_service['name']} • "
                        f"{chosen_date.strftime('%d.%m.%Y')} ob {chosen_time}"
                    )

        with tab2:
            st.markdown("### Ponudba salona")
            services = get_services(selected["id"])
            employees = get_employees(selected["id"])

            if services:
                df_services = pd.DataFrame(
                    [
                        {
                            "Storitev": s["name"],
                            "Kategorija": s["category"],
                            "Trajanje (min)": s["duration_min"],
                            "Cena (€)": s["price_eur"],
                        }
                        for s in services
                    ]
                )
                st.dataframe(df_services, use_container_width=True, hide_index=True)

            if employees:
                df_employees = pd.DataFrame(
                    [{"Ime": e["name"], "Vloga": e["role"]} for e in employees]
                )
                st.dataframe(df_employees, use_container_width=True, hide_index=True)

        with tab3:
            st.markdown("### Ocene uporabnikov")
            reviews = get_reviews(selected["id"])

            for rev in reviews:
                with st.container(border=True):
                    st.write(f"**{rev['customer_name']}** — {'⭐' * rev['stars']}")
                    if rev.get("comment"):
                        st.write(rev["comment"])

            st.markdown("#### Dodaj oceno")
            review_name = st.text_input("Tvoje ime", value=st.session_state["user"]["full_name"])
            stars = st.slider("Ocena", min_value=1, max_value=5, value=5)
            comment = st.text_area("Komentar")

            if st.button("Objavi oceno"):
                add_review(selected["id"], review_name.strip(), stars, comment.strip())
                st.success("Ocena je bila dodana.")
                st.rerun()

    with right:
        st.markdown('<div class="small-card">', unsafe_allow_html=True)
        st.markdown("### Hitri pregled")
        st.write(f"**Prijavljen:** {st.session_state['user']['full_name']}")
        st.write(f"**E-pošta:** {st.session_state['user']['email']}")
        my_count = len(get_user_bookings(st.session_state["user"]["id"]))
        st.write(f"**Moje rezervacije:** {my_count}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="small-card">
                <h4 style="margin-top:0;">Promo kotiček</h4>
                <p style="color:#4b5563;">
                    Tukaj lahko kasneje dodaš banner, akcijo, sponzorja, kodo za popust ali karkoli drugega.
                </p>
                <p style="font-weight:700; margin-bottom:0;">Primer: Koda UREDIME10 za 10% popusta</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def profile_page():
    render_header()

    user = st.session_state["user"]
    bookings = get_user_bookings(user["id"])

    col1, col2 = st.columns([1.2, 2.3])

    with col1:
        st.markdown('<div class="profile-box">', unsafe_allow_html=True)
        st.markdown("### Moj profil")
        st.write(f"**Ime:** {user['full_name']}")
        st.write(f"**E-pošta:** {user['email']}")
        st.write(f"**Število rezervacij:** {len(bookings)}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("### Moje rezervacije")
        if bookings:
            df = pd.DataFrame(bookings)
            df = df.rename(
                columns={
                    "salon_name": "Salon",
                    "city": "Mesto",
                    "employee_name": "Zaposleni",
                    "service_name": "Storitev",
                    "price_eur": "Cena (€)",
                    "booking_date": "Datum",
                    "booking_time": "Ura",
                    "status": "Status",
                }
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Še nimaš nobene rezervacije.")


# -------------------------
# APP
# -------------------------
def main():
    setup_page()
    init_db()

    if "user" not in st.session_state:
        st.session_state["user"] = None

    st.sidebar.markdown("## UrediMe")
    st.sidebar.caption("Beauty booking platform")
    render_sidebar_ad()

    if st.session_state["user"] is None:
        auth_view()
        return

    st.sidebar.write(f"Prijavljen: **{st.session_state['user']['full_name']}**")

    page = st.sidebar.radio("Navigacija", ["Rezervacije", "Moj profil"])

    if st.sidebar.button("Odjava"):
        st.session_state["user"] = None
        st.rerun()

    if page == "Rezervacije":
        bookings_page()
    else:
        profile_page()


if __name__ == "__main__":
    main()
