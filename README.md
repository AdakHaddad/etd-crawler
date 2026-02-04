# ETD UGM Crawler

Tool untuk mengakses dan mendownload dokumen full-text PDF dari repositori Electronic Theses and Dissertations (ETD) Universitas Gadjah Mada.

## 📋 Persyaratan

- Terhubung ke jaringan **UGM-hotspot** atau jaringan yang sama dengan ETD Perpustakaan Pusat UGM
- Python 3.x (opsional, jika menggunakan script)
- Browser modern

## 🔍 Cara Kerja

### Langkah 1: Cari Publikasi
Cari nama publikasi/thesis/disertasi yang diinginkan melalui Google dengan query:
```
site:etd.repository.ugm.ac.id "judul publikasi"
```

### Langkah 2: Dapatkan ID Dokumen
1. Buka halaman hasil pencarian dari ETD UGM
2. Hover atau copy link download PDF dari bagian yang tersedia secara publik:
   - Abstrak
   - Halaman Judul
   - Daftar Isi
   - Bibliografi
3. Perhatikan format URL, contoh:
   ```
   https://etd.repository.ugm.ac.id/downloadfile/XXXXX
   ```
   Di mana `XXXXX` adalah ID dokumen

### Langkah 3: Crawl ID Full-text
ID dokumen full-text biasanya berada di sekitar ID dokumen yang sudah ditemukan. Lakukan pencarian dengan range ID:

```bash
# Contoh: jika ID abstrak adalah 123456, coba range sekitar ID tersebut
for i in {123450..123470}; do
    echo "Checking ID: $i"
    curl -s -o /dev/null -w "%{http_code}" "https://etd.repository.ugm.ac.id/downloadfile/$i"
    echo ""
done
```

### Langkah 4: Download Full-text
Setelah menemukan ID yang valid (HTTP 200), download file:
```bash
curl -O "https://etd.repository.ugm.ac.id/downloadfile/[ID_YANG_DITEMUKAN]"
```

## 💡 Tips

- ID full-text biasanya berdekatan dengan ID abstrak/judul/daftar isi
- Dalam beberapa kasus, ID full-text bisa terpisah jauh dari ID dokumen publik
- Gunakan script untuk mempercepat proses pencarian range ID
- Pastikan terhubung ke jaringan internal UGM

## 📁 Struktur Proyek

```
etd-ugm-crawler/
├── README.md
├── crawler.py          # Script utama (opsional)
├── requirements.txt    # Dependencies (opsional)
└── examples/           # Contoh penggunaan
```

## ⚠️ Disclaimer

> **PENTING: Repositori ini dibuat untuk tujuan penelitian dan edukasi (educational purpose only).**

Kami percaya bahwa ilmu pengetahuan seharusnya dapat diakses secara **gratis dan mudah bagi semua orang** — sesuai dengan filosofi **UGM Kerakyatan**.

### Catatan Penting:
- 📧 Kami telah melaporkan kerentanan ini ke email Perpustakaan UGM dan DTI (Direktorat Teknologi Informasi)
- 🕐 Hingga tanggal commit terakhir, metode ini masih berfungsi
- 🎓 Gunakan dengan bijak dan bertanggung jawab
- 📚 Hormati hak cipta dan ketentuan penggunaan yang berlaku

## 🤝 Kontribusi

Kontribusi, issue, dan feature request sangat diterima. Silakan buat issue atau pull request.

## 📜 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE) — lihat file LICENSE untuk detail.

---

**"Ilmu yang bermanfaat adalah ilmu yang dibagikan"** 🎓

*Made with ❤️ for open knowledge*
