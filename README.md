# 📖 Dataset Kamus Bahasa Palembang (Slang ke Baku)

Repository ini berisi dataset *open-source* pemetaan kosakata bahasa gaul/sehari-hari Palembang ke dalam Bahasa Indonesia baku. 

Dataset ini sangat cocok digunakan sebagai kamus *slang words* untuk tahapan *text preprocessing* (normalisasi teks) dalam penelitian *Data Science*, *Text Mining*, maupun *Natural Language Processing* (NLP) seperti *Sentiment Analysis* pada data media sosial atau ulasan *e-commerce*.

## 📂 Struktur Data

Data utama tersimpan di dalam file `kamus_palembang.csv`. File ini terdiri dari dua kolom utama:

- `kata_gaul`: Kosakata bahasa Palembang sehari-hari, singkatan, atau bahasa slang (contoh: *ad*, *adek*, *pacak*).
- `kata_baku`: Terjemahan atau padanan katanya dalam Bahasa Indonesia standar (contoh: *ada*, *adik*, *bisa*).

**Contoh isi dataset:**
| kata_gaul | kata_baku |
| :--- | :--- |
| acung | acung |
| ad | ada |
| adek | adik |

## 🚀 Cara Penggunaan (Python/Pandas)

Jika kamu ingin menggunakan dataset ini di Google Colab atau *environment* Python lainnya untuk mengubah teks slang menjadi baku, kamu bisa menggunakan contoh kode Pandas berikut:

```python
import pandas as pd

# Load dataset
df_kamus = pd.read_csv('kamus_palembang.csv')

# Buat dictionary untuk mapping
slang_dict = dict(zip(df_kamus['kata_gaul'], df_kamus['kata_baku']))

# Contoh fungsi normalisasi teks
def normalisasi_teks(teks):
    kata_kata = teks.split()
    kata_normal = [slang_dict.get(kata, kata) for kata in kata_kata]
    return " ".join(kata_normal)

# Test fungsi
teks_kotor = "adek ad di rumah"
teks_bersih = normalisasi_teks(teks_kotor)
print(teks_bersih) # Output: adik ada di rumah
