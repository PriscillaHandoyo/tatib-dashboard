import hashlib
import streamlit as st
from db.mongodb import get_db

st.title("Tatib Paroki St. Yakobus Kelapa Gading")

db = get_db()
lingkungan_collection = db["lingkungan"]

# add a form to login
if "page" not in st.session_state:
    st.session_state.page = "main"

def login():
    st.session_state.page = "login"

def main():
    st.session_state.page = "main"

def admin():
    st.session_state.page = "admin"

def user_dashboard(nama):
    st.session_state.page = "user"
    st.session_state.lingkungan_nama = nama

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
            st.session_state.page = "admin"
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

elif st.session_state.page == "admin":
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

elif st.session_state.page == "user":
    nama = st.session_state.get("lingkungan_nama", "")
    lingkungan = lingkungan_collection.find_one({"nama": nama})
    st.header(f"Selamat datang, Lingkungan {nama}!")
    if lingkungan:
        st.write(f"Nama Ketua: {lingkungan.get('ketua', '-')}")
        st.write(f"Jumlah Tatib: {lingkungan.get('jumlah_tatib', '-')}")
    else:
        st.error("Data lingkungan tidak ditemukan.")
    if st.button("Logout", key="user_logout", on_click=main):
        st.session_state.page = "main"
        st.rerun()