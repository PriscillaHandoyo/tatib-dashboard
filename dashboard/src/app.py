import hashlib
import streamlit as st
from db.mongodb import get_db
from urllib.parse import urlencode, parse_qs

st.title("Tatib Paroki St. Yakobus Kelapa Gading")

db = get_db()
lingkungan_collection = db["lingkungan"]

# add a form to login
query_params = st.query_params
if "page" in query_params:
    st.session_state.page = query_params["page"]
elif "page" not in st.session_state:
    st.session_state.page = "main"

def set_page(page_name):
    st.session_state.page = page_name
    st.query_params["page"] = page_name

def login():
    set_page("login")

def main():
    set_page("main")

def admin():
    set_page("admin")
    st.query_params["admin"] = "true"

def user_dashboard(nama):
    set_page("user")
    st.session_state.lingkungan_nama = nama
    st.query_params["lingkungan_nama"] = nama

# -------------------------------------------------------------------------------
# ADD LINGKUNGAN 
# Tambah lingkungan --> db
# Login --> login page
if st.session_state.page == "main":
    # add a form to add new lingkungan
    st.header("Tambah Lingkungan Baru")
    nama = st.text_input("Nama Lingkungan")
    ketua = st.text_input("Nama Ketua Lingkungan")
    jumlah_tatib = st.number_input("Jumlah Tatib", min_value=0, step=1)
    password = st.text_input("Password", type="password")

    if st.button("Tambah Lingkungan"):
        if nama and ketua and jumlah_tatib >= 0 and password:
            # check if lingkungan already exists
            if lingkungan_collection.find_one({"nama": nama}):
                st.error("Lingkungan sudah terdaftar. Silahkan Login atau gunakan nama lain.")
            else:
                hashed_pw = hashlib.sha256(password.encode()).hexdigest()
                lingkungan_collection.insert_one({
                    "nama": nama,
                    "ketua": ketua,
                    "jumlah_tatib": jumlah_tatib,
                    "password": hashed_pw
                })
                st.success("Lingkungan berhasil ditambahkan!")
                st.rerun()
        else:
            st.error("Semua field harus diisi.")
        
    if st.button("Login", key="main_login", on_click=login):
        login()

# -------------------------------------------------------------------------------
# LOGIN PAGE
# Login (Main Page) clicked --> Login Page
elif st.session_state.page == "login":
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
    
    if st.button("Kembali", key="back_to_main", on_click=main):
        st.session_state.page = "main"

# -------------------------------------------------------------------------------
# ADMIN DASHBOARD
elif st.session_state.page == "admin":
    # check if admin state is in query params (for refreshing the page)
    if st.query_params.get("admin", "") == "true":
        # sidebar navigation
        with st.sidebar:
            st.header("Menu")
            st.markdown("Availability")
            st.markdown("Info Lingkungan")
            st.markdown("----")
            st.button("Logout", key="user_logout", on_click=main)

        st.header("Admin Dashboard")
        st.write("Selamat datang di dashboard, Admin!")

        # display all lingkungan
        lingkungan_list = list(lingkungan_collection.find())
        if lingkungan_list:
            st.write("Daftar Lingkungan:")
            st.table([{k: v for k, v in lingkungan.items() if k != "_id" and k != "password"} for lingkungan in lingkungan_list])
        else:
            st.write("Tidak ada data lingkungan yang tersedia.")
        if st.button("Logout", key="admin_logout", on_click=main):
            st.session_state.page = "main"
            st.rerun()

# -------------------------------------------------------------------------------
# USER DASHBOARD
elif st.session_state.page == "user":
    nama = st.session_state.get("lingkungan_nama", st.query_params.get("lingkungan_nama", ""))
    lingkungan = lingkungan_collection.find_one({"nama": nama})

    # sidebar navigation
    with st.sidebar:
        st.header("Menu")
        st.markdown("Availability")
        st.markdown("Info Lingkungan")
        st.markdown("----")
        st.button("Logout", key="user_logout", on_click=main)

    st.header(f"Selamat datang, Lingkungan {nama}!")
    if lingkungan:
        col1, col2, col3 = st.columns(3)
        col1.metric("Jumlah Tatib", lingkungan.get("jumlah_tatib", 0))
        col2.metric("Nama Ketua", lingkungan.get("ketua", "-"))
        col3.metric("Lingkungan", nama)

        st.subheader("Tatib Analytics")
        # Example chart (replace with your own data)
        import pandas as pd
        import numpy as np
        df = pd.DataFrame({
            "Bulan": ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul"],
            "Tatib": np.random.randint(0, 10, 7)
        })
        st.line_chart(df.set_index("Bulan"))

        st.subheader("Tatib List")
        # Example table (replace with your own data)
        st.table(df)
    else:
        st.error("Data lingkungan tidak ditemukan.")

