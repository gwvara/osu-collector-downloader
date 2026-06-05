# 🎵 osu! Beatmap Collection Downloader

Download beatmap dari koleksi [osu!Collector](https://osucollector.com/) secara otomatis, tanpa perlu login atau buka browser.

## ✨ Fitur

- 📋 **Baca collection** dari osu!Collector via URL atau ID
- 📥 **Pilih jumlah** beatmap yang mau didownload
- 🚫 **Tanpa video** — otomatis download versi no-video (hemat bandwidth)
- 🔄 **Mirror fallback** — Nerinyan → catboy.best
- ⚡ **Download paralel** — hingga 5 download sekaligus
- 🔁 **Auto retry** — 3x percobaan per mirror dengan exponential backoff
- ⏭️ **Skip existing** — lewati beatmap yang sudah ada
- 📊 **Progress bar** — tampilan progress real-time di terminal
- 📁 **Auto-detect** folder osu! Songs

## 📋 Persyaratan

- **Python 3.8+** — [Download Python](https://python.org/downloads/)
  - ⚠️ Saat install, centang **"Add Python to PATH"**
- **Koneksi internet**

## 🚀 Cara Pakai

### 1. Install Dependencies
Klik dua kali `install.bat` atau jalankan:
```bash
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi
Klik dua kali `run.bat` atau jalankan:
```bash
python main.py
```

### 3. Ikuti Langkah-langkah
1. Masukkan URL collection, contoh:
   ```
   https://osucollector.com/collections/21770/CARBONE'S-AIM-COLLECTION
   ```
2. Pilih berapa beatmapset yang mau didownload (atau ketik `all`)
3. Tentukan folder tujuan (otomatis detect folder osu! Songs)
4. Set jumlah download paralel (default: 3)
5. Konfirmasi dan tunggu download selesai!

## 📁 Struktur File

```
aplikasiosu/
├── main.py          # Entry point aplikasi
├── collector.py     # Fetch data dari osu!Collector API
├── downloader.py    # Download beatmap dari mirror
├── utils.py         # Utility functions
├── requirements.txt # Dependencies
├── install.bat      # Installer (Windows)
├── run.bat          # Launcher (Windows)
└── README.md        # Dokumentasi
```

## ⚙️ Mirror Servers

| Mirror | URL | No Video |
|--------|-----|----------|
| Nerinyan | `api.nerinyan.moe` | ✅ `?noVideo=1` |
| catboy.best | `catboy.best` | ✅ `?noVideo` |

Aplikasi secara otomatis mencoba mirror pertama, jika gagal akan fallback ke mirror berikutnya.

## ❓ FAQ

**Q: Apakah perlu login osu!?**
A: Tidak! Aplikasi menggunakan mirror server yang tidak memerlukan autentikasi.

**Q: Apakah file .osz otomatis muncul di osu!?**

A: Ya, cukup buka/restart osu! dan beatmap baru akan otomatis diimport.

**Q: Download gagal terus, kenapa?**
A: Kemungkinan rate limiting dari mirror server. Coba kurangi jumlah download paralel ke 1-2, atau tunggu beberapa menit.

**Q: Bisa download koleksi lebih dari 1000 beatmap?**
A: Bisa! Tapi disarankan download bertahap untuk menghindari rate limiting.


## Tujuan Proyek

Proyek ini dibuat sebagai sarana pembelajaran dan eksplorasi dalam bidang:

- Pengembangan aplikasi desktop
- Integrasi API
- Otomasi proses download
- Manajemen file
- Pengolahan data dari web service
- Implementasi alur kerja berbasis workflow

Selain itu, aplikasi ini juga menjadi solusi praktis untuk mempercepat proses pengumpulan beatmap dari osu!Collector ke dalam osu! (karena tidak ada dana untuk donate osu!collector).
