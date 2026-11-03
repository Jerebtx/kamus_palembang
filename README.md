# Kamus Normalisasi Dialek Palembang (Versi Beku)

Repositori ini berisi sumber daya pendukung artikel:

> Siahaan, J. A., Indah, D. R., Ariani, A., Syahbani, M. H., & Ibrahim, A. *Normalisasi Leksikal Dialek Palembang pada Analisis Sentimen Berbasis Aspek Car Free Day Menggunakan IndoBERT.* MALCOM: Indonesian Journal of Machine Learning and Computer Science (dalam proses terbit).

Isinya adalah kamus normalisasi dialek Palembang yang dipakai pada eksperimen, skrip pembekuannya, dan pedoman anotasi sentimen.

## Isi repositori

| File / folder | Keterangan |
| --- | --- |
| `kamus_palembang_beku_v2.csv` | **Kamus yang dipakai pada eksperimen.** Berisi 472 entri, dibekukan hanya dari data latih. |
| `fase1v2_kamus_beku.py` | Skrip pembekuan kamus (dijalankan di Google Colab). |
| `pedoman_anotasi.pdf` | Pedoman anotasi sentimen (Negatif, Netral, Positif) beserta aturan kasus sulit. |
| `versi_awal/kamus_palembang.csv` | Kamus lengkap sebelum pembekuan (2.103 entri). **Tidak dipakai pada eksperimen**; disimpan sebagai arsip. |

## Kolom kamus beku

| Kolom | Arti |
| --- | --- |
| `kata_gaul` | Bentuk dialek atau tidak baku yang dinormalisasi |
| `kata_baku` | Bentuk baku pengganti |
| `jenis` | `dialek`, `singkatan`, `informal umum`, atau `pemanjangan` |
| `frek_latih` | Frekuensi kemunculan pada data latih |
| `n_dok_latih` | Jumlah komentar data latih yang memuat kata tersebut |
| `dikoreksi` | `True` untuk dua entri yang dikoreksi sebelum eksperimen (*ktk* → "tidak ada", *nnyo* → "tanya") |

Komposisi: 329 dialek, 78 singkatan, 56 informal umum, dan 9 pemanjangan huruf.

## Cara kamus dibekukan

1. Seluruh korpus (4.372 komentar) dibagi lebih dulu menjadi data latih, validasi, dan uji berbasis unggahan (3.155 / 389 / 828 komentar). Pembagian dikunci sebelum kamus dibekukan.
2. Kamus lengkap diterapkan **hanya pada data latih**, setelah normalisasi dengan Colloquial Indonesian Lexicon (github.com/nasalsabila/kamus-alay).
3. Entri dipertahankan hanya bila kata asalnya muncul pada data latih dan entri tersebut benar-benar mengubah kata. Kata yang hanya muncul pada data validasi atau uji tidak masuk kamus.
4. Dua entri yang keliru dikoreksi sebelum eksperimen, lalu kamus dikunci dan tidak diubah lagi setelah hasil eksperimen dilihat.

Urutan penerapan pada pra-pemrosesan: *case folding* dan pembersihan teks → kamus gaul umum → kamus Palembang beku → penghapusan *stopword* minimal (kata negasi dipertahankan).

## Catatan data

Komentar mentah Instagram dan TikTok **tidak dibagikan** untuk melindungi privasi pengguna dan mematuhi ketentuan platform. Karena itu, skrip pembekuan disertakan untuk menunjukkan prosedurnya, tetapi tidak dapat dijalankan ulang tanpa data tersebut.

## Lisensi

Kamus dan pedoman dapat digunakan untuk keperluan penelitian dengan mencantumkan sitasi artikel di atas.
