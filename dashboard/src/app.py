from datetime import datetime
import hashlib
from components.logic import logic
import streamlit as st
from db.mongodb import get_db
from streamlit_calendar import calendar
import pandas as pd
import json
import calendar as pycalendar
import random

st.set_page_config(layout="wide") 

st.title("Tatib Paroki St. Yakobus Kelapa Gading")

db = get_db()
lingkungan_collection = db["lingkungan"]

natal_assignments_collection = db["natal_assignments"]
paskah_assignments_collection = db["paskah_assignments"]

# add a form to login
query_params = st.query_params
if "page" in query_params:
    st.session_state.page = query_params["page"]
elif "page" not in st.session_state:
    st.session_state.page = "login"

def set_page(page_name):
    st.session_state.page = page_name
    st.query_params["page"] = page_name

def login():
    set_page("login")
    st.query_params.pop("admin", None)
    st.query_params.pop("lingkungan_nama", None)

def admin():
    set_page("admin")
    st.query_params["admin"] = "true"

def form_lingkungan():
    set_page("form_lingkungan")

def data_lingkungan():
    set_page("data_linkungan")

def kalender_penugasan():
    set_page("kalender_penugasan")

def ml_penugasan():
    set_page("ml_penugasan")

def paskah_penugasan():
    set_page("paskah_penugasan")

# -------------------------------------------------------------------------------
# LOGIN PAGE
# Login (Main Page) clicked --> Login Page
if st.session_state.page == "login":
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # TESTING CREDENTIALS
    # Agnes 3, test123
    
    login_clicked = st.button("Login", key="login_submit")
    if login_clicked:
        # admin login check
        if username == "Admin" and password == "admin": # admin login details
            admin()
            st.rerun()
        else:
            st.error("Login gagal. Silahkan coba lagi.")

# -------------------------------------------------------------------------------
# ADMIN DASHBOARD
elif st.session_state.page == "admin":
    # check if admin state is in query params (for refreshing the page)
    if st.query_params.get("admin", "") == "true":
        # sidebar navigation
        with st.sidebar:
            st.header("Menu")
            if st.button("Dashboard", key="dashboard_btn", on_click=admin): pass
            if st.button("Form Lingkungan", key="form_lingkungan_btn", on_click=form_lingkungan): pass
            if st.button("Kalender Penugasan", key="kalender_btn", on_click=kalender_penugasan): pass
            if st.button("Paskah", key="paskah_btn", on_click=paskah_penugasan): pass
            if st.button("Misa Lainnya", key="ml_btn", on_click=ml_penugasan): pass
            if st.button("Data Lingkungan", key="data_lingkungan_btn", on_click=data_lingkungan): pass
            st.markdown("----")
            st.button("Logout", key="admin_logout", on_click=login)

        st.header("Admin Dashboard")
        st.write("Selamat datang di dashboard, Admin!")

# -------------------------------------------------------------------------------
# FORM LINGKUNGAN
elif st.session_state.page == "form_lingkungan":
    # Reset form fields if needed
    if st.session_state.get("reset_form", False):
        st.session_state["Nama Lingkungan"] = ""
        st.session_state["Nama Ketua Lingkungan"] = ""
        st.session_state["Jumlah Tatib"] = 0
        st.session_state["Gereja St. Yakbus: Sabtu"] = []
        st.session_state["Gereja St. Yakbus: Minggu"] = []
        st.session_state["Pegangsaan 2: Minggu"] = []
        st.session_state["reset_form"] = False

    st.header("Tambah Lingkungan Baru")
    nama = st.text_input("Nama Lingkungan", key="Nama Lingkungan")
    ketua = st.text_input("Nama Ketua Lingkungan", key="Nama Ketua Lingkungan")
    jumlah_tatib = st.number_input("Jumlah Tatib", min_value=0, step=1, key="Jumlah Tatib")
    
    st.subheader("Availability")
    yakobus_sabtu = st.multiselect(
        "Gereja St. Yakbus: Sabtu",
        ["17.00"],
        key="Gereja St. Yakbus: Sabtu"
    )
    yakobus_minggu = st.multiselect(
        "Gereja St. Yakbus: Minggu",
        ["08.00", "11.00", "17.00"],
        key="Gereja St. Yakbus: Minggu"
    )
    p2_minggu = st.multiselect(
        "Pegangsaan 2: Minggu",
        ["07.30", "10.30"],
        key="Pegangsaan 2: Minggu"
    )

    # sidebar navigation
    with st.sidebar:
        st.header("Menu")
        if st.button("Dashboard", key="dashboard_btn", on_click=admin): pass
        if st.button("Form Lingkungan", key="form_lingkungan_btn", on_click=form_lingkungan): pass
        if st.button("Kalender Penugasan", key="kalender_btn", on_click=kalender_penugasan): pass
        if st.button("Paskah", key="paskah_btn", on_click=paskah_penugasan): pass
        if st.button("Misa Lainnya", key="ml_btn", on_click=ml_penugasan): pass
        if st.button("Data Lingkungan", key="data_lingkungan_btn", on_click=data_lingkungan): pass
        st.markdown("----")
        st.button("Logout", key="admin_logout", on_click=login)

    if st.button("Tambah Lingkungan"):
        if nama and ketua and jumlah_tatib >= 0:
            if lingkungan_collection.find_one({"nama": nama}):
                st.error("Lingkungan sudah terdaftar. Silahkan Login atau gunakan nama lain.")
            else:
                lingkungan_collection.insert_one({
                    "nama": nama,
                    "ketua": ketua,
                    "jumlah_tatib": jumlah_tatib,
                    "availability": {
                        "yakobus_sabtu": yakobus_sabtu,
                        "yakobus_minggu": yakobus_minggu,
                        "p2_minggu": p2_minggu
                    }
                })
                st.success("Lingkungan berhasil ditambahkan!")
                # Set flag to reset form fields on next rerun
                st.session_state["reset_form"] = True
                st.rerun()
        else:
            st.error("Semua field harus diisi.")

# -------------------------------------------------------------------------------
# KALENDER PENUGASAN
elif st.session_state.page == "kalender_penugasan":
    st.header("Tabel Penugasan Bulanan")

    # Month/year selector
    today = datetime.today()
    selected_year = st.number_input("Tahun", min_value=2020, max_value=2100, value=today.year, step=1)
    selected_month = st.selectbox(
        "Bulan",
        options=list(range(1, 13)),
        format_func=lambda x: datetime(1900, x, 1).strftime('%B'),
        index=today.month-1
    )

    st.info("Gunakan pilihan bulan/tahun di atas untuk mengganti penugasan.")

    st.subheader(f"Penugasan Bulan {selected_month}-{selected_year}")

    lingkungan_list = list(lingkungan_collection.find())
    lingkungan_names = [l['nama'] for l in lingkungan_list]

    # Generate slots for selected month/year
    cal = pycalendar.Calendar()
    saturdays = [d for d in cal.itermonthdates(selected_year, selected_month) if d.weekday() == 5 and d.month == selected_month]
    sundays = [d for d in cal.itermonthdates(selected_year, selected_month) if d.weekday() == 6 and d.month == selected_month]

    jam_misa_sabtu = ["17.00"]
    jam_misa_minggu = ["08.00", "11.00", "17.00"]
    jam_misa_p2 = ["07.30", "10.30"]

    # Prepare all slot keys for the month
    slot_keys = []
    for date in saturdays:
        slot_keys.append(f"{date.strftime('%Y-%m-%d')}T17.00:00")
    for date in sundays:
        slot_keys.extend([
            f"{date.strftime('%Y-%m-%d')}T08.00:00",
            f"{date.strftime('%Y-%m-%d')}T11.00:00",
            f"{date.strftime('%Y-%m-%d')}T17.00:00",
            f"{date.strftime('%Y-%m-%d')}T07.30:00",
            f"{date.strftime('%Y-%m-%d')}T10.30:00"
        ])

    # Assign each lingkungan only once per month, randomized
    if (
        "assign_logic" not in st.session_state
        or st.session_state.get("assign_logic_month") != selected_month
        or st.session_state.get("assign_logic_year") != selected_year
    ):
        assign_logic = {}
        lingkungan_pool = lingkungan_names.copy()
        random.shuffle(lingkungan_pool)
        # Only assign each lingkungan once per month
        for i, slot_key in enumerate(slot_keys):
            if lingkungan_pool:
                assign_logic[slot_key] = [lingkungan_pool.pop()]
            else:
                assign_logic[slot_key] = []  # Leave empty if all lingkungan already assigned
        st.session_state.assign_logic = assign_logic
        st.session_state.assign_logic_month = selected_month
        st.session_state.assign_logic_year = selected_year

    def get_assignment(date, jam):
        slot_key = f"{date.strftime('%Y-%m-%d')}T{jam}:00"
        return ", ".join(st.session_state.assign_logic.get(slot_key, []))

    def render_aligned_table(date, jam_list, lingkungan_list):
        st.markdown(
            "<table style='width:100%'><tr><th>Jam Misa</th><th>Lingkungan</th><th>Randomize</th></tr>",
            unsafe_allow_html=True
        )
        for jam in jam_list:
            slot_key = f"{date.strftime('%Y-%m-%d')}T{jam}:00"
            lingkungan_val = ", ".join(st.session_state.assign_logic.get(slot_key, []))
            cols = st.columns([2, 4, 2])
            cols[0].markdown(f"<div style='text-align:center'>{jam}</div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div style='text-align:center'>{lingkungan_val}</div>", unsafe_allow_html=True)
            button_key = f"randomize_{slot_key}"

            # Find lingkungan already assigned for this month
            assigned_lingkungan = set()
            for v in st.session_state.assign_logic.values():
                assigned_lingkungan.update(v)
            # Only allow lingkungan not yet assigned this month
            available_lingkungan = [l for l in lingkungan_names if l not in assigned_lingkungan or l == lingkungan_val]

            if cols[2].button("Randomize", key=button_key):
                # Remove current assignment from available_lingkungan so it can be replaced
                if lingkungan_val:
                    available_lingkungan = [l for l in available_lingkungan if l != lingkungan_val]
                if available_lingkungan:
                    random_lingkungan = random.choice(available_lingkungan)
                    st.session_state.assign_logic[slot_key] = [random_lingkungan]
                    st.success(f"Randomized: {random_lingkungan} for {jam} on {date.strftime('%d-%m-%Y')}")
                    st.rerun()
                else:
                    st.warning("There are no other lingkungan available for this month.")
        st.markdown("</table>", unsafe_allow_html=True)

    # Display tables for Saturdays
    st.subheader("Sabtu")
    for date in saturdays:
        st.markdown(f"**{date.strftime('%d-%m-%Y')} (Sabtu)**")
        render_aligned_table(date, jam_misa_sabtu, lingkungan_list)

    # Display tables for Sundays (Yakobus)
    st.subheader("Minggu (Yakobus)")
    for date in sundays:
        st.markdown(f"**{date.strftime('%d-%m-%Y')} (Minggu Yakobus)**")
        render_aligned_table(date, jam_misa_minggu, lingkungan_list)

    # Display tables for Sundays (P2)
    st.subheader("Minggu (Stasi P2)")
    for date in sundays:
        st.markdown(f"**{date.strftime('%d-%m-%Y')} (Minggu Stasi P2)**")
        render_aligned_table(date, jam_misa_p2, lingkungan_list)

    # sidebar navigation
    with st.sidebar:
        st.header("Menu")
        if st.button("Dashboard", key="dashboard_btn", on_click=admin): pass
        if st.button("Form Lingkungan", key="form_lingkungan_btn", on_click=form_lingkungan): pass
        if st.button("Kalender Penugasan", key="kalender_btn", on_click=kalender_penugasan): pass
        if st.button("Paskah", key="paskah_btn", on_click=paskah_penugasan): pass
        if st.button("Misa Lainnya", key="ml_btn", on_click=ml_penugasan): pass
        if st.button("Data Lingkungan", key="data_lingkungan_btn", on_click=data_lingkungan): pass
        st.markdown("----")
        st.button("Logout", key="admin_logout", on_click=login)

# -------------------------------------------------------------------------------
# PASKAH
elif st.session_state.page == "paskah_penugasan":
    st.header("Penugasan Khusus (Paskah)")
    event_date = st.date_input("Tanggal Event")
    slot_times_ra = st.text_input("Jam Slot: Rabu Abu (pisahkan dengan koma, contoh: 06.00, 09.00, 11.00)")
    slot_times_mp = st.text_input("Jam Slot: Minggu Palma (pisahkan dengan koma, contoh: 06.00, 09.00, 11.00)")
    slot_times_kp = st.text_input("Jam Slot: Kamis Putih (pisahkan dengan koma, contoh: 06.00, 09.00, 11.00)")
    slot_times_ja = st.text_input("Jam Slot: Jumat Agung (pisahkan dengan koma, contoh: 06.00, 09.00, 11.00)")
    slot_times_sc = st.text_input("Jam Slot: Sabtu Suci (pisahkan dengan koma, contoh: 06.00, 09.00, 11.00)")
    slot_times_mpas = st.text_input("Jam Slot: Minggu Paskah (pisahkan dengan koma, contoh: 06.00, 09.00, 11.00)")
    slot_capacity = st.number_input("Jumlah Tatib per Slot", min_value=1, value=40)
    
    lingkungan_list = list(lingkungan_collection.find())

    # Load assignments from DB
    saved = paskah_assignments_collection.find_one({"_id": "paskah"})
    assignments = saved["assignments"] if saved else {}

    if st.button("Buat Penugasan"):
        all_slots = []
        if slot_times_ra:
            all_slots += [f"{event_date.strftime('%Y-%m-%d')}T{jam.strip()}:00 Rabu Abu" for jam in slot_times_ra.split(",") if jam.strip()]
        if slot_times_mp:
            all_slots += [f"{event_date.strftime('%Y-%m-%d')}T{jam.strip()}:00 Minggu Palma" for jam in slot_times_mp.split(",") if jam.strip()]
        if slot_times_kp:
            all_slots += [f"{event_date.strftime('%Y-%m-%d')}T{jam.strip()}:00 Kamis Putih" for jam in slot_times_kp.split(",") if jam.strip()]
        if slot_times_ja:
            all_slots += [f"{event_date.strftime('%Y-%m-%d')}T{jam.strip()}:00 Jumat Agung" for jam in slot_times_ja.split(",") if jam.strip()]
        if slot_times_sc:
            all_slots += [f"{event_date.strftime('%Y-%m-%d')}T{jam.strip()}:00 Sabtu Suci" for jam in slot_times_sc.split(",") if jam.strip()]
        if slot_times_mpas:
            all_slots += [f"{event_date.strftime('%Y-%m-%d')}T{jam.strip()}:00 Minggu Paskah" for jam in slot_times_mpas.split(",") if jam.strip()]
        
        assignments = {}
        lingkungan_idx = 0
        n_lingkungan = len(lingkungan_list)
        for slot in all_slots:
            assignments[slot] = []
            total_people = 0
            count = 0
            while total_people < slot_capacity and count < n_lingkungan:
                l = lingkungan_list[lingkungan_idx % n_lingkungan]
                if l['nama'] not in [nama for slot_list in assignments.values() for nama in slot_list]:
                    assignments[slot].append(l['nama'])
                    total_people += l['jumlah_tatib']
                    lingkungan_idx += 1
                    count += 1
                else:
                    lingkungan_idx += 1
                    count += 1
        # Save to DB
        paskah_assignments_collection.replace_one(
            {"_id": "paskah"},
            {"_id": "paskah", "assignments": assignments},
            upsert=True
        )

    # Delete Table button
    if st.button("Hapus Tabel Penugasan"):
        paskah_assignments_collection.delete_one({"_id": "paskah"})
        assignments = {}

    # Display assignments in table if exists
    if assignments:
        st.write("Tabel Penugasan:")
        for slot, names in assignments.items():
            st.write(f"**{slot}**")
            st.table(pd.DataFrame({"Lingkungan": names}))

    # sidebar navigation
    with st.sidebar:
        st.header("Menu")
        if st.button("Dashboard", key="dashboard_btn", on_click=admin): pass
        if st.button("Form Lingkungan", key="form_lingkungan_btn", on_click=form_lingkungan): pass
        if st.button("Kalender Penugasan", key="kalender_btn", on_click=kalender_penugasan): pass
        if st.button("Paskah", key="paskah_btn", on_click=paskah_penugasan): pass
        if st.button("Misa Lainnya", key="ml_btn", on_click=ml_penugasan): pass
        if st.button("Data Lingkungan", key="data_lingkungan_btn", on_click=data_lingkungan): pass
        st.markdown("----")
        st.button("Logout", key="admin_logout", on_click=login)

# -------------------------------------------------------------------------------
# MISA LAINNYA
elif st.session_state.page == "ml_penugasan":
    st.header("Penugasan Khusus (Misa Lainnya)")
    event_date = st.date_input("Tanggal Event")
    slot_times = st.text_input("Jam Slot (pisahkan dengan koma, contoh: 06.00, 09.00, 11.00)")
    slot_capacity = st.number_input("Jumlah Tatib per Slot", min_value=1, value=40)
    lingkungan_list = list(lingkungan_collection.find())

    # Load assignments from DB
    saved = natal_assignments_collection.find_one({"_id": "natal"})
    assignments = saved["assignments"] if saved else {}

    if st.button("Buat Penugasan"):
        slots = [f"{event_date.strftime('%Y-%m-%d')}T{jam.strip()}:00" for jam in slot_times.split(",") if jam.strip()]
        assignments = {}
        lingkungan_idx = 0
        n_lingkungan = len(lingkungan_list)
        for slot in slots:
            assignments[slot] = []
            total_people = 0
            count = 0
            while total_people < slot_capacity and count < n_lingkungan:
                l = lingkungan_list[lingkungan_idx % n_lingkungan]
                if l['nama'] not in [nama for slot_list in assignments.values() for nama in slot_list]:
                    assignments[slot].append(l['nama'])
                    total_people += l['jumlah_tatib']
                    lingkungan_idx += 1
                    count += 1
                else:
                    lingkungan_idx += 1
                    count += 1
        # Save to DB
        natal_assignments_collection.replace_one(
            {"_id": "natal"},
            {"_id": "natal", "assignments": assignments},
            upsert=True
        )

    # Delete Table button
    if st.button("Hapus Tabel Penugasan"):
        natal_assignments_collection.delete_one({"_id": "natal"})
        assignments = {}

    # Display assignments in table if exists
    if assignments:
        st.write("Tabel Penugasan:")
        for slot, names in assignments.items():
            st.write(f"**{slot}**")
            st.table(pd.DataFrame({"Lingkungan": names}))

    # sidebar navigation
    with st.sidebar:
        st.header("Menu")
        if st.button("Dashboard", key="dashboard_btn", on_click=admin): pass
        if st.button("Form Lingkungan", key="form_lingkungan_btn", on_click=form_lingkungan): pass
        if st.button("Kalender Penugasan", key="kalender_btn", on_click=kalender_penugasan): pass
        if st.button("Paskah", key="paskah_btn", on_click=paskah_penugasan): pass
        if st.button("Misa Lainnya", key="ml_btn", on_click=ml_penugasan): pass
        if st.button("Data Lingkungan", key="data_lingkungan_btn", on_click=data_lingkungan): pass
        st.markdown("----")
        st.button("Logout", key="admin_logout", on_click=login)

# -------------------------------------------------------------------------------
# DATA LINGKUNGAN
elif st.session_state.page == "data_linkungan":
    # sidebar navigation
    with st.sidebar:
        st.header("Menu")
        if st.button("Dashboard", key="dashboard_btn", on_click=admin): pass
        if st.button("Form Lingkungan", key="form_lingkungan_btn", on_click=form_lingkungan): pass
        if st.button("Kalender Penugasan", key="kalender_btn", on_click=kalender_penugasan): pass
        if st.button("Paskah", key="paskah_btn", on_click=paskah_penugasan): pass
        if st.button("Misa Lainnya", key="ml_btn", on_click=ml_penugasan): pass
        if st.button("Data Lingkungan", key="data_lingkungan_btn", on_click=data_lingkungan): pass
        st.markdown("----")
        st.button("Logout", key="admin_logout", on_click=login)

    st.header("Data Lingkungan")

    # search bar
    search_query = st.text_input("Cari Lingkungan (nama):").lower()

    # define all possible slots
    slots = [
        ("yakobus_sabtu", "17.00", "Yakobus Sabtu 17.00"),
        ("yakobus_minggu", "08.00", "Yakobus Minggu 08.00"),
        ("yakobus_minggu", "11.00", "Yakobus Minggu 11.00"),
        ("yakobus_minggu", "17.00", "Yakobus Minggu 17.00"),
        ("p2_minggu", "07.30", "P2 Minggu 07.30"),
        ("p2_minggu", "10.30", "P2 Minggu 10.30"),
    ]

    # display all lingkungan
    lingkungan_list = list(lingkungan_collection.find())
    if search_query:
        lingkungan_list = [l for l in lingkungan_list if search_query in l.get("nama", "").lower()]

    if lingkungan_list:
        st.markdown("""
        <style>
        .st-emotion-cache-1y4p8pa {padding: 0;}
        .st-emotion-cache-1y4p8pa button {margin: 0 2px;}
        .st-emotion-cache-1y4p8pa div {text-align: center;}
        </style>
        """, unsafe_allow_html=True)
        st.write("### Tabel Lingkungan")

        # Table header
        cols = ["Update", "Delete", "Nama", "Ketua", "Jumlah Tatib"] + [slot[2] for slot in slots]
        header = st.columns(len(cols))
        for i, col_name in enumerate(cols):
            header[i].markdown(f"<b>{col_name}</b>", unsafe_allow_html=True)

        # Table rows
        for lingkungan in lingkungan_list:
            avail = lingkungan.get("availability", {})
            if isinstance(avail, str):
                try:
                    avail = json.loads(avail)
                except Exception:
                    avail = {}
            col_update, col_delete, *col_rest = st.columns(len(cols))
            # Update button
            if col_update.button("✏️", key=f"update_{lingkungan['_id']}"):
                st.session_state[f"edit_{lingkungan['_id']}"] = True
            # Delete button
            if col_delete.button("🗑️", key=f"delete_{lingkungan['_id']}"):
                lingkungan_collection.delete_one({"_id": lingkungan["_id"]})
                st.warning(f"Lingkungan {lingkungan.get('nama','')} berhasil dihapus!")
                st.rerun()
            # Edit form
            if st.session_state.get(f"edit_{lingkungan['_id']}", False):
                new_ketua = col_rest[1].text_input("", value=lingkungan.get("ketua",""), key=f"edit_ketua_{lingkungan['_id']}")
                new_jumlah = col_rest[2].number_input("", min_value=0, value=int(lingkungan.get("jumlah_tatib",0)), key=f"edit_jumlah_{lingkungan['_id']}")

                # Availability editing
                new_avail = {}
                # Track which slot_types have already been rendered
                rendered_types = set()
                for idx, (slot_type, slot_time, slot_label) in enumerate(slots):
                    if slot_type not in rendered_types:
                        if slot_type == "yakobus_sabtu":
                            options = ["17.00"]
                        elif slot_type == "yakobus_minggu":
                            options = ["08.00", "11.00", "17.00"]
                        elif slot_type == "p2_minggu":
                            options = ["07.30", "10.30"]
                        else:
                            options = []
                        current_times = avail.get(slot_type, [])
                        new_avail[slot_type] = col_rest[3+idx].multiselect(
                            f"{slot_label.split()[0]}",
                            options,
                            default=current_times,
                            key=f"edit_avail_{slot_type}_{lingkungan['_id']}"
                        )
                        rendered_types.add(slot_type)

                # Place the save button ONCE per row, after all multiselects
                if col_update.button("💾 Simpan", key=f"save_{lingkungan['_id']}"):
                    lingkungan_collection.update_one(
                        {"_id": lingkungan["_id"]},
                        {"$set": {
                            "ketua": new_ketua,
                            "jumlah_tatib": new_jumlah,
                            "availability": new_avail
                        }}
                    )
                    st.success("Data lingkungan berhasil diupdate!")
                    st.session_state[f"edit_{lingkungan['_id']}"] = False
                    st.rerun()
                col_rest[0].write(lingkungan.get("nama", ""))
            else:
                col_rest[0].write(lingkungan.get("nama", ""))
                col_rest[1].write(lingkungan.get("ketua", ""))
                col_rest[2].write(lingkungan.get("jumlah_tatib", ""))
            # Availability columns
            for idx, (slot_type, slot_time, _) in enumerate(slots):
                times = avail.get(slot_type, [])
                status = "✅" if slot_time in times else "❌"
                col_rest[3+idx].markdown(f"<span style='font-size:18px'>{status}</span>", unsafe_allow_html=True)
    else:
        st.write("Tidak ada data lingkungan yang tersedia.")