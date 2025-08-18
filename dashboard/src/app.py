import streamlit as st
from db.mongodb import get_db

st.title("Tatib Paroki St. Yakobus Kelapa Gading")

db = get_db()
lingkungan_collection = db["lingkungan"]

# fetch all lingkungan data
lingkungan_list = list(lingkungan_collection.find())

if lingkungan_list:
    st.write("Daftar Lingkungan:")
    st.table([{k: v for k, v in lingkungan.items() if k != "_id"} for lingkungan in lingkungan_list])
else:
    st.write("Tidak ada data lingkungan yang tersedia.")

# add a form to add new lingkungan
st.header("Tambah Lingkungan Baru")
nama = st.text_input("Nama Lingkungan")
ketua = st.text_input("Nama Ketua Lingkungan")
jumlah_tatib = st.number_input("Jumlah Tatib", min_value=0, step=1)

if st.button("Tambah Lingkungan"):
    if nama and ketua and jumlah_tatib >= 0:
        lingkungan_collection.insert_one({
            "nama": nama,
            "ketua": ketua,
            "jumlah_tatib": jumlah_tatib
        })
        st.success("Lingkungan berhasil ditambahkan!")
        st.rerun()
    else:
        st.error("Semua field harus diisi dengan benar.")