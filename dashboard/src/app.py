import hashlib
import streamlit as st
from db.mongodb import get_db
from streamlit_calendar import calendar

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

def user_dashboard(nama):
    set_page("user")
    st.session_state.lingkungan_nama = nama
    st.query_params["lingkungan_nama"] = nama

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
    login_nama = st.text_input("Nama Lingkungan")
    login_password = st.text_input("Password", type="password")

    # TESTING CREDENTIALS
    # Agnes 3, test123
    
    login_clicked = st.button("Login", key="login_submit")
    if login_clicked:
        # admin login check
        if login_nama == "Admin" and login_password == "admin": # admin login details
            admin()
            st.rerun()
        else:
            lingkungan = lingkungan_collection.find_one({"nama": login_nama})
            if lingkungan:
                hashed_pw = hashlib.sha256(login_password.encode()).hexdigest()
                if lingkungan.get("password") == hashed_pw:
                    user_dashboard(login_nama)
                    st.rerun()
                else:
                    st.error("Silahkan periksa nama atau password Anda.")
            else:
                st.error("Lingkungan tidak ditemukan. Silahkan daftar terlebih dahulu.")
    
    if st.button("Kembali", key="back_to_login", on_click=login):
        # st.session_state.page = "login"
        pass

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
    st.header("Tambah Lingkungan Baru")
    nama = st.text_input("Nama Lingkungan")
    ketua = st.text_input("Nama Ketua Lingkungan")
    jumlah_tatib = st.number_input("Jumlah Tatib", min_value=0, step=1)
    
    st.subheader("Availability")

    # Yakobus
    yakobus_sabtu = st.multiselect(
        "Gereja St. Yakbus: Sabtu",
        ["17.00"]
    )
    yakobus_minggu = st.multiselect(
        "Gereja St. Yakbus: Minggu",
        ["08.00", "11.00", "17.00"]
    )

    # Pegangsaan 2
    p2_minggu = st.multiselect(
        "Pegangsaan 2: Minggu",
        ["07.30", "10.30"]
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
                st.rerun()
        else:
            st.error("Semua field harus diisi.")

    if st.button("Kembali ke Admin", key="back_to_admin", on_click=admin):
        pass

# -------------------------------------------------------------------------------
# KALENDER PENUGASAN
elif st.session_state.page == "kalender_penugasan":
    st.header("Kalender Penugasan")

    calendar_options = {
        "editable": True,
        "selectable": True,
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "timeGridDay,timeGridWeek,dayGridMonth"
        }
    }
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

    # display all lingkungan
    lingkungan_list = list(lingkungan_collection.find())
    if lingkungan_list:
        st.table([{k: v for k, v in lingkungan.items() if k != "_id" and k != "password"} for lingkungan in lingkungan_list])
    else:
        st.write("Tidak ada data lingkungan yang tersedia.")