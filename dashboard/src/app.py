from datetime import datetime
import hashlib
from components.logic import logic
import streamlit as st
from db.mongodb import get_db
from streamlit_calendar import calendar
import pandas as pd
import json

st.set_page_config(layout="wide") 

st.title("Tatib Paroki St. Yakobus Kelapa Gading")

db = get_db()
lingkungan_collection = db["lingkungan"]

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
            if st.button("Dashboard", key="dashboard_btn", on_click=admin):
                pass
            if st.button("Form Lingkungan", key="form_lingkungan_btn", on_click=form_lingkungan):
                pass
            if st.button("Kalender Penugasan", key="kalender_btn", on_click=kalender_penugasan):
                pass
            if st.button("Data Lingkungan", key="data_lingkungan_btn", on_click=data_lingkungan):
                pass
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
        if st.button("Dashboard", key="dashboard_btn", on_click=admin):
            pass
        if st.button("Form Lingkungan", key="form_lingkungan_btn", on_click=form_lingkungan):
            pass
        if st.button("Kalender Penugasan", key="kalender_btn", on_click=kalender_penugasan):
            pass
        if st.button("Data Lingkungan", key="data_lingkungan_btn", on_click=data_lingkungan):
            pass
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
    st.header("Kalender Penugasan")

    today = datetime.today()
    year = today.year
    month = today.month

    # get all lingkungan
    lingkungan_list = list(lingkungan_collection.find())

    # prepare events for calendar
    penugasan = []
    for lingkungan in lingkungan_list:
        nama = lingkungan.get("nama", "")
        availability = lingkungan.get("availability", {})

        # yakobus sabtu
        for jam in availability.get("yakobus_sabtu", []):
            penugasan.append({
                "title": f"{nama} - Yakobus Sabtu",
                "start": f"2025-08-01T{jam.replace('.',':')}:00",
                "end": f"2025-08-01T{jam.replace('.',':')}:59"
            })
        # yakobus minggu
        for jam in availability.get("yakobus_minggu", []):
            penugasan.append({
                "title": f"{nama} - Yakobus Minggu",
                "start": f"2025-08-02T{jam.replace('.',':')}:00",  
                "end": f"2025-08-02T{jam.replace('.',':')}:59"
            })
        # pegangsaan 2 minggu
        for jam in availability.get("p2_minggu", []):
            penugasan.append({
                "title": f"{nama} - Pegangsaan 2 Minggu",
                "start": f"2025-08-02T{jam.replace('.',':')}:00",  
                "end": f"2025-08-02T{jam.replace('.',':')}:59"
            })

    calendar_options = {
        "editable": True,
        "selectable": True,
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "timeGridDay,timeGridWeek,dayGridMonth"
        },
        "events": penugasan,
    }

    assign_logic = logic(
        lingkungan_list=lingkungan_list,
        year=year,  # Example year, adjust as needed
        month=month,  # Example month, adjust as needed
        available_slots={
            "2025-08-01T17:00:00": 20,
            "2025-08-02T08:00:00": 20,
            "2025-08-02T11:00:00": 20,
            "2025-08-02T17:00:00": 20,
            "2025-08-02T07:30:00": 20,
            "2025-08-02T10:30:00": 20
        }
    )

    penugasan = []
    for slot, lingkungan_names in assign_logic.items():
        for nama in lingkungan_names:
            penugasan.append({
                "title": f"{nama}",
                "start": slot,
                "end": slot  # You can add duration if needed
            })
    
    calendar_options["events"] = penugasan
    calendar_events = calendar(options=calendar_options)

    # sidebar navigation
    with st.sidebar:
        st.header("Menu")
        if st.button("Dashboard", key="dashboard_btn", on_click=admin):
            pass
        if st.button("Form Lingkungan", key="form_lingkungan_btn", on_click=form_lingkungan):
            pass
        if st.button("Kalender Penugasan", key="kalender_btn", on_click=kalender_penugasan):
            pass
        if st.button("Data Lingkungan", key="data_lingkungan_btn", on_click=data_lingkungan):
            pass
        st.markdown("----")
        st.button("Logout", key="admin_logout", on_click=login)

# -------------------------------------------------------------------------------
# DATA LINGKUNGAN
elif st.session_state.page == "data_linkungan":
    # sidebar navigation
    with st.sidebar:
        st.header("Menu")
        if st.button("Dashboard", key="dashboard_btn", on_click=admin):
            pass
        if st.button("Form Lingkungan", key="form_lingkungan_btn", on_click=form_lingkungan):
            pass
        if st.button("Kalender Penugasan", key="kalender_btn", on_click=kalender_penugasan):
            pass
        if st.button("Data Lingkungan", key="data_lingkungan_btn", on_click=data_lingkungan):
            pass
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