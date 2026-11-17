# Prediksi Pola Kedatangan Wisatawan Mancanegara di Sumatera Utara
### Menggunakan Regresi Polinomial Berbasis Python

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://wisman-sumut-polynomial-regression-sfyzwvbzjgdzzdveczvpay.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-polyfit-013243?logo=numpy&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌐 Demo Aplikasi

**🔗 [Buka Aplikasi →](https://wisman-sumut-polynomial-regression-sfyzwvbzjgdzzdveczvpay.streamlit.app/)**

> Gunakan akun demo atau daftar akun baru untuk mengakses dashboard.

---

## 📋 Deskripsi

Aplikasi web interaktif berbasis **Python + Streamlit** untuk menganalisis dan memprediksi pola kedatangan wisatawan mancanegara (wisman) di Provinsi Sumatera Utara menggunakan metode **Regresi Polinomial**.

Data bersumber dari **Badan Pusat Statistik (BPS) Provinsi Sumatera Utara**, mencakup tiga pintu masuk internasional:

| Pintu Masuk | Jenis | Keterangan |
|---|---|---|
| Bandara Kualanamu | Udara | Pintu masuk utama |
| Pelabuhan Teluk Nibung | Laut | Tanjungbalai |
| Pelabuhan Belawan | Laut | Medan |

**Periode data:** Januari 2024 – September 2026 (33 bulan)

---

## ✨ Fitur

### 📑 Data Historis
- Tabel data kunjungan wisman per bulan per pintu masuk
- Statistik deskriptif (min, max, mean, median, std, koef. variasi)
- Pie chart distribusi per pintu masuk
- Time-series chart interaktif semua pintu masuk
- Export data ke CSV

### 🧮 Model Regresi Polinomial
- Pemilihan derajat polinomial (Degree 1–6) via slider
- Persamaan model dengan notasi matematika (Ŷ = a₀xⁿ + ...)
- Evaluasi model: R², RMSE, MAE, MAPE
- Chart fitting aktual vs kurva regresi
- Plot residual (bar chart warna merah/hijau)
- Tabel perbandingan semua degree (1–6) secara bersamaan
- Catatan otomatis jika R² rendah

### 🔮 Prediksi Masa Depan
- Proyeksi 1–24 bulan ke depan
- Chart gabungan: historis + fitting + proyeksi
- Tabel proyeksi dengan indikator tren (↗/↘)
- Ringkasan statistik proyeksi
- Export proyeksi ke CSV

### 📊 Analisis Pola Kedatangan
- **Pola musiman** — rata-rata per bulan (dari tahun data lengkap)
- **Perbandingan tahunan** — overlay 2024, 2025, 2026
- **Heatmap** kunjungan bulan × tahun
- **Regresi per pintu masuk** — model individual Kualanamu, Teluk Nibung, Belawan
- **Stacked bar chart** komposisi kunjungan

### ℹ️ Tentang Sistem
- Latar belakang penelitian
- Penjelasan metode OLS
- Stack teknologi lengkap
- Sumber data

### 🔐 Autentikasi
- Registrasi dan login pengguna
- Password di-hash dengan SHA-256 + salt
- Penyimpanan menggunakan SQLite

---

## 🧮 Metode

Model regresi polinomial memetakan variabel waktu **x** (periode urut, 1 = Jan 2024) ke estimasi jumlah wisman **Ŷ**:

```
Ŷ = a₀xⁿ + a₁xⁿ⁻¹ + a₂xⁿ⁻² + ... + aₙ
```

Koefisien dihitung dengan **Ordinary Least Squares (OLS)** menggunakan `numpy.polyfit`. Model dievaluasi dengan:

| Metrik | Keterangan |
|---|---|
| **R²** | Proporsi variansi yang dijelaskan model |
| **RMSE** | Root Mean Square Error (satuan orang) |
| **MAE** | Mean Absolute Error |
| **MAPE** | Mean Absolute Percentage Error |

---

## 🛠️ Stack Teknologi

| Library | Fungsi |
|---|---|
| `streamlit` | Framework web app interaktif |
| `numpy` | Kalkulasi regresi polinomial (`polyfit`) |
| `pandas` | Manipulasi dan analisis dataset |
| `scikit-learn` | Kalkulasi metrik evaluasi (R², RMSE) |
| `plotly` | Visualisasi interaktif |
| `sqlite3` | Database autentikasi pengguna |
| `hashlib` | Hashing password (SHA-256 + salt) |
| `openpyxl` | Pembacaan dataset Excel BPS |

---

## 🚀 Cara Menjalankan Lokal

### 1. Clone repository

```bash
git clone https://github.com/ra6341170-jpg/wisman-sumut-polynomial-regression.git
cd wisman-sumut-polynomial-regression
```

### 2. Buat virtual environment (opsional tapi disarankan)

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 3. Install dependensi

```bash
pip install -r requirements.txt
```

### 4. Jalankan aplikasi

```bash
streamlit run app.py
```

Aplikasi akan terbuka di `http://localhost:8501`

---

## 📁 Struktur Proyek

```
wisman-sumut-polynomial-regression/
│
├── app.py              # Entry point — konfigurasi halaman & routing
├── auth.py             # Halaman login & registrasi
├── dashboard.py        # Seluruh logika dashboard & visualisasi
├── database.py         # Fungsi SQLite: init, register, login
├── requirements.txt    # Dependensi Python
│
├── data/
│   └── dataset_wisman_sumut_2024_2026.xlsx   # Dataset BPS Sumut
│
└── users.db            # Database SQLite (auto-generated)
```

---

## 📊 Dataset

| Atribut | Detail |
|---|---|
| Sumber | BPS Provinsi Sumatera Utara |
| Periode | Januari 2024 – September 2026 |
| Jumlah baris | 33 bulan |
| Kolom | Periode (X), Tahun, Bulan, Kualanamu, Teluk Nibung, Belawan, Total Wisman (Y) |

---

## 📝 Catatan Akademis

Nilai R² model polinomial pada dataset ini relatif rendah (< 0.50 untuk degree 1–4). Ini bukan kesalahan implementasi, melainkan **karakteristik data pariwisata** yang sangat dipengaruhi fluktuasi musiman, hari libur, dan faktor eksternal yang tidak dapat dimodelkan oleh fungsi polinomial sederhana. Degree 5–6 memberikan R² lebih baik namun berisiko *overfitting* untuk proyeksi jangka panjang.

---

## 📄 Lisensi

MIT License — bebas digunakan untuk keperluan akademis dan penelitian.

---
  Data: BPS Provinsi Sumatera Utara &nbsp;·&nbsp; 2026
</p>
