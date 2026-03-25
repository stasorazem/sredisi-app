import sqlite3
from datetime import datetime, date, timedelta

import pandas as pd
import streamlit as st

DB_PATH = "slo_sredime.db"


# -------------------------
# Database helpers
# -------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

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
            salon_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            customer_phone TEXT,
            customer_email TEXT,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'rezervirano',
            created_at TEXT NOT NULL,
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
        (
            "Studio Lepota Koper",
            "Koper",
            "Frizerski in kozmetični salon",
            "Pristaniška ulica 12, Koper",
            "Moderen salon za striženje, barvanje, nego obraza in nohte.",
            4.8,
            "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f",
        ),
        (
            "Morski SPA Izola",
            "Izola",
            "SPA in masaže",
            "Veliki trg 4, Izola",
            "Sprostitveni tretmaji, masaže in wellness paketi.",
            4.6,
            "https://images.unsplash.com/photo-1515377905703-c4788e51af15",
        ),
        (
            "Ljubljana Glow Bar",
            "Ljubljana",
            "Nail & beauty",
            "Trubarjeva 22, Ljubljana",
            "Manikira, pedikira, lash lift in hitri beauty tretmaji.",
            4.9,
            "https://images.unsplash.com/photo-1604654894610-df63bc536371",
        ),
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
        (salon_map["Studio Lepota Koper"], "Sara", "Kozmetičarka"),
        (salon_map["Morski SPA Izola"], "Marko", "Maser"),
        (salon_map["Morski SPA Izola"], "Tina", "Wellness terapevtka"),
        (salon_map["Ljubljana Glow Bar"], "Ana", "Nail artist"),
        (salon_map["Ljubljana Glow Bar"], "Maja", "Beauty specialist"),
    ]
    cur.executemany(
        "INSERT INTO employees (salon_id, name, role) VALUES (?, ?, ?)", employees
    )

    services = [
        (salon_map["Studio Lepota Koper"], "Žensko striženje", 60, 32.0, "Frizerstvo"),
        (salon_map["Studio Lepota Koper"], "Barvanje las", 120, 58.0, "Frizerstvo"),
        (salon_map["Studio Lepota Koper"], "Nega obraza", 75, 45.0, "Kozmetika"),
        (salon_map["Morski SPA Izola"], "Klasična masaža", 50, 42.0, "Masaže"),
        (salon_map["Morski SPA Izola"], "Antistres paket", 80, 65.0, "SPA"),
        (salon_map["Ljubljana Glow Bar"], "Gel manikira", 60, 35.0, "Nail"),
        (salon_map["Ljubljana Glow Bar"], "Pedikira", 50, 33.0, "Nail"),
        (salon_map["Ljubljana Glow Bar"], "Lash lift", 45, 39.0, "Beauty"),
    ]
    cur.executemany(
        """
        INSERT INTO services (salon_id, name, duration_min, price_eur, category)
        VALUES (?, ?, ?, ?, ?)
        """,
        services,
    )

    reviews = [
        (
            salon_map["Studio Lepota Koper"],
            "Petra",
            5,
            "Zelo prijazni in točni.",
            datetime.now().isoformat(),
        ),
        (
            salon_map["Morski SPA Izola"],
            "Matej",
            4,
            "Odlična masaža in lep ambient.",
            datetime.now().isoformat(),
        ),
        (
            salon_map["Ljubljana Glow Bar"],
            "Nika",
            5,
            "Top nohti, zelo priporočam.",
            datetime.now().isoformat(),
        ),
    ]
    cur.executemany(
        """
        INSERT INTO reviews (salon_id, customer_name, stars, comment, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        reviews,
    )

    conn.commit()


def fetch_all(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def execute(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


# -------------------------
# Business logic
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
    if search:
        query += " AND (name LIKE ? OR description LIKE ? OR address LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like, like])

    query += " ORDER BY rating DESC, name ASC"
    return fetch_all(query, tuple(params))


def get_employees(salon_id):
    return fetch_all(
        "SELECT * FROM employees WHERE salon_id = ? ORDER BY name ASC", (salon_id,)
    )


def get_services(salon_id):
    return fetch_all(
        "SELECT * FROM services WHERE salon_id = ? ORDER BY category, name ASC",
        (salon_id,),
    )


def get_reviews(salon_id):
    return fetch_all(
        "SELECT * FROM reviews WHERE salon_id = ? ORDER BY id DESC", (salon_id,)
    )


def get_available_times(employee_id, booking_date, service_duration=60):
    start_hour = 8
    end_hour = 19
    slots = []

    current = datetime.combine(booking_date, datetime.min.time()).replace(
        hour=start_hour, minute=0
    )
    end_dt = datetime.combine(booking_date, datetime.min.time()).replace(
        hour=end_hour, minute=0
    )

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
            booking_date, datetime.strptime(row["booking_time"], "%H:%M").time()
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


def create_booking(
    salon_id,
    employee_id,
    service_id,
    customer_name,
    customer_phone,
    customer_email,
    booking_date,
    booking_time,
):
    return execute(
        """
        INSERT INTO bookings (
            salon_id, employee_id, service_id,
            customer_name, customer_phone, customer_email,
            booking_date, booking_time, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'rezervirano', ?)
        """,
        (
            salon_id,
            employee_id,
            service_id,
            customer_name,
            customer_phone,
            customer_email,
            booking_date.isoformat(),
            booking_time,
            datetime.now().isoformat(),
        ),
    )


def update_salon_rating(salon_id):
    rows = fetch_all(
        "SELECT AVG(stars) AS avg_stars FROM reviews WHERE salon_id = ?", (salon_id,)
    )
    avg = rows[0]["avg_stars"] if rows and rows[0]["avg_stars"] is not None else 0
    execute("UPDATE salons SET rating = ? WHERE id = ?", (round(avg, 1), salon_id))


def add_review(salon_id, customer_name, stars, comment):
    execute(
        """
        INSERT INTO reviews (salon_id, customer_name, stars, comment, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (salon_id, customer_name, stars, comment, datetime.now().isoformat()),
    )
    update_salon_rating(salon_id)


def get_dashboard_bookings(salon_id=None):
    query = """
        SELECT b.id, s.name AS salon_name, e.name AS employee_name,
               sv.name AS service_name, sv.price_eur,
               b.customer_name, b.customer_phone, b.customer_email,
               b.booking_date, b.booking_time, b.status
        FROM bookings b
        JOIN salons s ON s.id = b.salon_id
        JOIN employees e ON e.id = b.employee_id
        JOIN services sv ON sv.id = b.service_id
        WHERE 1=1
    """
    params = []
    if salon_id:
        query += " AND b.salon_id = ?"
        params.append(salon_id)
    query += " ORDER BY b.booking_date ASC, b.booking_time ASC"
    return fetch_all(query, tuple(params))


# -------------------------
# UI helpers
# -------------------------
def salon_card(salon):
    with st.container(border=True):
        col1, col2 = st.columns([1.2, 2])
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


def main_page():
    st.title("UrediMe 🇸🇮")
    st.caption(
        "Slovenska MVP verzija za iskanje in rezervacijo terminov v salonih lepote, SPA centrih in wellness studiih."
    )

    cities = ["Vsa mesta"] + [
        r["city"] for r in fetch_all("SELECT DISTINCT city FROM salons ORDER BY city")
    ]
    categories = ["Vse kategorije"] + [
        r["category"]
        for r in fetch_all("SELECT DISTINCT category FROM salons ORDER BY category")
    ]

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

    salon_labels = [
        f"{s['name']} ({s['city']}) ⭐ {s['rating']}"
        for s in salons
    ]
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

            col1, col2 = st.columns(2)
            with col1:
                chosen_employee_label = st.selectbox(
                    "Izberi zaposlenega",
                    employee_labels,
                )
            with col2:
                chosen_service_label = st.selectbox(
                    "Izberi storitev",
                    service_labels,
                )

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

            st.markdown("#### Podatki stranke")
            customer_name = st.text_input("Ime in priimek")
            customer_phone = st.text_input("Telefon")
            customer_email = st.text_input("E-pošta")

            if st.button("Potrdi rezervacijo", type="primary", disabled=chosen_time is None):
                if not customer_name.strip():
                    st.warning("Prosimo, vnesi ime in priimek.")
                else:
                    booking_id = create_booking(
                        selected["id"],
                        chosen_employee["id"],
                        chosen_service["id"],
                        customer_name.strip(),
                        customer_phone.strip(),
                        customer_email.strip(),
                        chosen_date,
                        chosen_time,
                    )
                    st.success(f"Rezervacija uspešno ustvarjena. ID rezervacije: #{booking_id}")
                    st.info(
                        f"{selected['name']} • {chosen_service['name']} • "
                        f"{chosen_date.strftime('%d.%m.%Y')} ob {chosen_time}"
                    )

    with tab2:
        st.markdown("### Ponudba salona")
        services = get_services(selected["id"])
        employees = get_employees(selected["id"])

        if services:
            st.markdown("#### Storitve")
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
            st.markdown("#### Zaposleni")
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
        review_name = st.text_input("Tvoje ime")
        stars = st.slider("Ocena", min_value=1, max_value=5, value=5)
        comment = st.text_area("Komentar")

        if st.button("Objavi oceno"):
            if review_name.strip():
                add_review(selected["id"], review_name.strip(), stars, comment.strip())
                st.success("Ocena je bila dodana.")
                st.rerun()
            else:
                st.warning("Prosimo, vnesi ime.")


def partner_dashboard():
    st.title("Partner nadzorna plošča")
    st.caption(
        "Osnovni del za salone: pregled rezervacij, dodajanje terminov, zaposlenih in storitev."
    )

    salons = fetch_all("SELECT * FROM salons ORDER BY name")
    if not salons:
        st.info("Ni vnešenih salonov.")
        return

    salon_labels = [s["name"] for s in salons]
    selected_label = st.selectbox("Izberi salon", salon_labels)
    selected_salon = salons[salon_labels.index(selected_label)]

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Rezervacije", "Dodaj storitev", "Dodaj zaposlenega", "Dodaj salon"]
    )

    with tab1:
        rows = get_dashboard_bookings(selected_salon["id"])
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Za ta salon še ni rezervacij.")

    with tab2:
        with st.form("service_form"):
            s_name = st.text_input("Naziv storitve")
            s_cat = st.text_input("Kategorija")
            s_dur = st.number_input(
                "Trajanje (min)", min_value=15, max_value=300, value=60, step=15
            )
            s_price = st.number_input(
                "Cena (€)", min_value=1.0, max_value=1000.0, value=30.0, step=1.0
            )
            submitted = st.form_submit_button("Dodaj storitev")
            if submitted:
                if s_name.strip():
                    execute(
                        """
                        INSERT INTO services (salon_id, name, duration_min, price_eur, category)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            selected_salon["id"],
                            s_name.strip(),
                            int(s_dur),
                            float(s_price),
                            s_cat.strip(),
                        ),
                    )
                    st.success("Storitev dodana.")
                    st.rerun()
                else:
                    st.warning("Naziv storitve je obvezen.")

    with tab3:
        with st.form("employee_form"):
            e_name = st.text_input("Ime zaposlenega")
            e_role = st.text_input("Vloga")
            submitted = st.form_submit_button("Dodaj zaposlenega")
            if submitted:
                if e_name.strip() and e_role.strip():
                    execute(
                        "INSERT INTO employees (salon_id, name, role) VALUES (?, ?, ?)",
                        (selected_salon["id"], e_name.strip(), e_role.strip()),
                    )
                    st.success("Zaposleni dodan.")
                    st.rerun()
                else:
                    st.warning("Ime in vloga sta obvezna.")

    with tab4:
        with st.form("salon_form"):
            name = st.text_input("Naziv salona")
            city = st.text_input("Mesto")
            category = st.text_input("Kategorija")
            address = st.text_input("Naslov")
            description = st.text_area("Opis")
            image_url = st.text_input("URL slike")
            submitted = st.form_submit_button("Dodaj salon")
            if submitted:
                if name.strip() and city.strip() and category.strip():
                    execute(
                        """
                        INSERT INTO salons (name, city, category, address, description, rating, image_url)
                        VALUES (?, ?, ?, ?, ?, 0, ?)
                        """,
                        (
                            name.strip(),
                            city.strip(),
                            category.strip(),
                            address.strip(),
                            description.strip(),
                            image_url.strip(),
                        ),
                    )
                    st.success("Salon dodan.")
                    st.rerun()
                else:
                    st.warning("Naziv, mesto in kategorija so obvezni.")


def setup_page():
    st.set_page_config(page_title="UrediMe", page_icon="✨", layout="wide")
    st.markdown(
        """
        <style>
            .stApp {max-width: 1400px; margin: 0 auto;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    setup_page()
    init_db()

    page = st.sidebar.radio("Navigacija", ["Uporabnik", "Partner"])
    st.sidebar.markdown("---")
    st.sidebar.write("**MVP funkcije**")
    st.sidebar.write("• iskanje salonov")
    st.sidebar.write("• filtriranje po mestu")
    st.sidebar.write("• rezervacija termina")
    st.sidebar.write("• izbira zaposlenega")
    st.sidebar.write("• ocene uporabnikov")
    st.sidebar.write("• partner dashboard")

    if page == "Uporabnik":
        main_page()
    else:
        partner_dashboard()


if __name__ == "__main__":
    main()
