import hashlib
import streamlit as st
from db.mongodb import get_db

st.title("Tatib Paroki St. Yakobus Kelapa Gading")

db = get_db()
lingkungan_collection = db["lingkungan"]

# display existing lingkungan
# fetch all lingkungan data
# lingkungan_list = list(lingkungan_collection.find())
# if lingkungan_list:
#     st.write("Daftar Lingkungan:")
#     st.table([{k: v for k, v in lingkungan.items() if k != "_id"} for lingkungan in lingkungan_list])
# else:
#     st.write("Tidak ada data lingkungan yang tersedia.")
    
# add a form to login
if "page" not in st.session_state:
    st.session_state.page = "main"

def login():
    st.session_state.page = "login"

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
        
    if st.button("Login", key="main_login"):
        login()

elif st.session_state.page == "login":
    st.header("Login")
    login_nama = st.text_input("Nama Lingkungan")
    login_password = st.text_input("Password", type="password")
    if st.button("Login", key="login_submit"):
        lingkungan = lingkungan_collection.find_one({"nama": login_nama})
        if lingkungan:
            hashed_pw = hashlib.sha256(login_password.encode()).hexdigest()
            if lingkungan.get("password") == hashed_pw:
                st.success(f"Selamat Datang, Lingkungan {login_nama}!")
            else:
                st.error("Silahkan periksa nama atau password Anda.")
        else:
            st.error("Lingkungan tidak ditemukan. Silahkan daftar terlebih dahulu.")
    
    if st.button("Kembali", key="back_to_main"):
        st.session_state.page = "main"