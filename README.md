# 🎵 osu!Collector Downloader

## Deskripsi

**osu!Collector Downloader** adalah aplikasi desktop yang dibuat untuk mempermudah proses pengunduhan beatmap dari website osu!Collector secara otomatis. Aplikasi ini memungkinkan pengguna untuk mengambil seluruh daftar beatmap dari sebuah koleksi, memilih jumlah map yang ingin diunduh, lalu langsung mengimpor hasil unduhan ke folder osu! tanpa perlu melakukannya satu per satu secara manual.

Proyek ini dibuat untuk mengatasi masalah proses pengunduhan beatmap yang memakan waktu ketika sebuah koleksi berisi puluhan hingga ratusan map.

---

## Latar Belakang

Ketika menemukan koleksi menarik di osu!Collector, pengguna biasanya harus:

1. Membuka halaman koleksi.
2. Membuka halaman beatmap satu per satu.
3. Mengunduh setiap beatmap secara manual.
4. Memindahkan file hasil unduhan ke folder osu!.
5. Mengulangi proses tersebut berkali-kali.

Jika koleksi berisi ratusan beatmap, proses ini menjadi sangat tidak efisien.

Melalui aplikasi ini, seluruh proses tersebut dapat dilakukan hanya dengan memasukkan URL koleksi dan menentukan jumlah beatmap yang ingin diunduh.

---

## Fitur Utama

### 📥 Download Beatmap dari osu!Collector

Aplikasi dapat mengambil seluruh daftar beatmap dari sebuah koleksi osu!Collector hanya menggunakan URL koleksi.

### 🚀 Download Massal

Mendukung pengunduhan banyak beatmap secara otomatis tanpa perlu membuka halaman beatmap satu per satu.

### 🎚 Filter Jumlah Beatmap

Pengguna dapat menentukan berapa banyak beatmap yang ingin diunduh.

Contoh:

- Koleksi berisi 500 beatmap
- Pengguna hanya ingin mengunduh 50 beatmap
- Aplikasi hanya akan memproses 50 beatmap pertama

### 📂 Integrasi Otomatis dengan osu!

Aplikasi akan mencoba mendeteksi folder `Songs` milik osu! secara otomatis.

Jika tidak ditemukan, pengguna dapat memilih folder tujuan secara manual.

### 🔄 Sistem Fallback Download

Apabila server utama gagal menyediakan file beatmap, aplikasi akan mencoba mengunduh dari sumber alternatif secara otomatis.

Hal ini meningkatkan tingkat keberhasilan proses download.

## Tujuan Proyek

Proyek ini dibuat sebagai sarana pembelajaran dan eksplorasi dalam bidang:

- Pengembangan aplikasi desktop
- Integrasi API
- Otomasi proses download
- Manajemen file
- Pengolahan data dari web service
- Implementasi alur kerja berbasis workflow
- Karena aku malas download map satu-satu
- Karena aku juga gapunya duit buat bayar osu!Collector hehe

Selain itu, aplikasi ini juga menjadi solusi praktis untuk mempercepat proses pengumpulan beatmap dari osu!Collector ke dalam osu! (karena terbatasnya budget ).
### 📊 Progress Bar

Pengguna dapat memantau progres pengunduhan secara real-time selama proses berlangsung.
