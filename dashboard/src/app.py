from datetime import datetime
import hashlib
from components.logic import logic
import streamlit as st
from db.mongodb import get_db
from streamlit_calendar import calendar
import pandas as pd
import json
import calendar as pycalendar

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

def natal_penugasan():
    set_page("natal_penugasan")

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
            if st.button("Natal", key="natal_btn", on_click=natal_penugasan): pass
            if st.button("Paskah", key="paskah_btn", on_click=paskah_penugasan): pass
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
        if st.button("Natal", key="natal_btn", on_click=natal_penugasan): pass
        if st.button("Paskah", key="paskah_btn", on_click=paskah_penugasan): pass
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
    st.header("Kalender Penugasan")

        # Month/year selector
    today = datetime.today()
    selected_year = st.number_input("Tahun", min_value=2020, max_value=2100, value=today.year, step=1)
    selected_month = st.selectbox(
        "Bulan",
        options=list(range(1, 13)),
        format_func=lambda x: datetime(1900, x, 1).strftime('%B'),
        index=today.month-1
    )

    # Add instruction banner
    st.info("Gunakan pilihan bulan/tahun di atas untuk mengganti penugasan. Tombol panah di kalender tidak aktif dan tidak mengubah data penugasan.")

    lingkungan_list = list(lingkungan_collection.find())

    # Generate slots for selected month/year
    cal = pycalendar.Calendar()
    saturdays = [d for d in cal.itermonthdates(selected_year, selected_month) if d.weekday() == 5 and d.month == selected_month]
    sundays = [d for d in cal.itermonthdates(selected_year, selected_month) if d.weekday() == 6 and d.month == selected_month]

    available_slots = {}
    for date in saturdays:
        available_slots[f"{date.strftime('%Y-%m-%d')}T17:00:00"] = 20
    for date in sundays:
        available_slots[f"{date.strftime('%Y-%m-%d')}T08:00:00"] = 20
        available_slots[f"{date.strftime('%Y-%m-%d')}T11:00:00"] = 20
        available_slots[f"{date.strftime('%Y-%m-%d')}T17:00:00"] = 20
        available_slots[f"{date.strftime('%Y-%m-%d')}T07:30:00"] = 20
        available_slots[f"{date.strftime('%Y-%m-%d')}T10:30:00"] = 20

    def get_global_rotation_idx(year, month, all_slots_per_month):
        # Calculate how many slots have been assigned before this month
        # For example, if each month has 8 slots, and you are in October (month=10), and you started in September (month=9):
        # total_slots_before = (month - start_month) * slots_per_month
        # If you want to start from January, use (month-1)
        return (year * 12 + month - 1) * all_slots_per_month

    slots_per_month = len(saturdays) + len(sundays) * 5  # adjust based on your slot generation
    rotation_idx = get_global_rotation_idx(selected_year, selected_month, slots_per_month)

    assign_logic, _ = logic(
        lingkungan_list=lingkungan_list,
        year=selected_year,
        month=selected_month,
        available_slots=available_slots,
        start_idx=rotation_idx
    )

    penugasan = []
    for slot, lingkungan_names in assign_logic.items():
        for nama in lingkungan_names:
            penugasan.append({
                "title": f"{nama}",
                "start": slot,
                "end": slot
            })

    calendar_options = {
        "editable": True,
        "selectable": True,
        "initialView": "dayGridMonth",
        "initialDate": f"{selected_year}-{selected_month:02d}-01",  # <-- Add this line
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "timeGridDay,timeGridWeek,dayGridMonth"
        },
        "events": penugasan,
    }

    st.markdown("""
    <style>
    .fc-header-toolbar{
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    calendar_events = calendar(options=calendar_options)

    # sidebar navigation
    with st.sidebar:
        st.header("Menu")
        if st.button("Dashboard", key="dashboard_btn", on_click=admin): pass
        if st.button("Form Lingkungan", key="form_lingkungan_btn", on_click=form_lingkungan): pass
        if st.button("Kalender Penugasan", key="kalender_btn", on_click=kalender_penugasan): pass
        if st.button("Natal", key="natal_btn", on_click=natal_penugasan): pass
        if st.button("Paskah", key="paskah_btn", on_click=paskah_penugasan): pass
        if st.button("Data Lingkungan", key="data_lingkungan_btn", on_click=data_lingkungan): pass
        st.markdown("----")
        st.button("Logout", key="admin_logout", on_click=login)

# -------------------------------------------------------------------------------
# NATAL 
elif st.session_state.page == "natal_penugasan":
    st.header("Penugasan Khusus (Natal)")
    event_date = st.date_input("Tanggal Event")
    slot_times = st.text_input("Jam Slot (pisahkan dengan koma, contoh: 06.00, 09.00, 11.00)")
    slot_capacity = st.number_input("Jumlah Tatib per Slot", min_value=1, value=40)
    
    lingkungan_list = list(lingkungan_collection.find())
    
    if st.button("Buat Penugasan"):
        slots = [f"{event_date.strftime('%Y-%m-%d')}T{jam.strip()}:00" for jam in slot_times.split(",")]
        assignments = {}
        lingkungan_idx = 0
        n_lingkungan = len(lingkungan_list)
        for slot in slots:
            assignments[slot] = []
            total_people = 0
            count = 0
            # Assign lingkungan in rotation, only once per event
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
        # Display assignments in table
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
        if st.button("Natal", key="natal_btn", on_click=natal_penugasan): pass
        if st.button("Paskah", key="paskah_btn", on_click=paskah_penugasan): pass
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
    
    if st.button("Buat Penugasan"):
        # Combine all slot times into one list
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
            # Assign lingkungan in rotation, only once per event
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
        # Display assignments in table
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
        if st.button("Natal", key="natal_btn", on_click=natal_penugasan): pass
        if st.button("Paskah", key="paskah_btn", on_click=paskah_penugasan): pass
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
        if st.button("Natal", key="natal_btn", on_click=natal_penugasan): pass
        if st.button("Paskah", key="paskah_btn", on_click=paskah_penugasan): pass
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