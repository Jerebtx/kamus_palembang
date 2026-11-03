# =====================================================================
# FASE 1 v2 - PEMBEKUAN KAMUS PALEMBANG DARI DATA LATIH SAJA
# Revisi MALCOM - Normalisasi Leksikal Dialek Palembang (skenario D)
#
# ATURAN C (DIKUNCI):
#  - Sumber pembekuan = komentar split 'latih' SAJA (validasi & uji tidak dipakai).
#  - Urutan pipeline tetap: cleaning -> kamus gaul -> kamus Palembang -> stopword
#    minimal. Entri dipertahankan bila kata asalnya muncul di data latih SETELAH
#    kamus gaul diterapkan dan entri tersebut benar-benar mengubah kata.
#  - Koreksi manual pra-eksperimen ktk & nnyo tetap berlaku (bila entrinya lolos).
#  - Setelah skrip ini, kamus TERKUNCI. Leksikon aspek TETAP (tidak diubah).
#  - S1/S2 dan aspek dihitung ulang untuk seluruh 4.382 komentar; korpus TIDAK
#    dipangkas ulang.
#
# MASUKAN (BASE = revisi_malcom_v2):
#   dari_v1/master_dataset_v2.csv
#   fase3d2_output/label_final_korpus_v2.csv   (setelah eksklusi tambahan)
#   fase3d2_output/split_v2.csv                (setelah eksklusi tambahan)
#   input_kamus/kamus_palembang.csv            (kamus asli, 2.103 baris)
#   input_kamus/kamus_palembang_beku_cek.csv   (kolom 'jenis' hasil cek manual v1)
#   input_kamus/jenis_tambahan.csv             (OPSIONAL: kata_gaul,jenis untuk entri baru)
#   input_kamus/kamus_gaul_indo.csv            (diunduh otomatis bila belum ada)
# KELUARAN: fase1v2_output/
#   kamus_palembang_beku_v2.csv, entri_tanpa_jenis.csv, perbandingan_kamus_v1_v2.csv,
#   entri_terbuang.csv, entri_tertimpa_gaul.csv, master_dataset_v3.csv, audit_fase1v2.txt
# =====================================================================


# %% SEL 1 - Mount & konfigurasi
import os, re, datetime, urllib.request
import numpy as np
import pandas as pd
from collections import Counter
try:
    from google.colab import drive
    drive.mount('/content/drive')
except Exception as e:
    print('Bukan di Colab / Drive tidak di-mount:', e)

BASE = '/content/drive/MyDrive/revisi_malcom_v2'
F_MASTER = f'{BASE}/dari_v1/master_dataset_v2.csv'
# Setelah eksklusi tambahan (fase3d2): split & label TANPA komentar yang dikeluarkan
F_LABEL = f'{BASE}/fase3d2_output/label_final_korpus_v2.csv'
F_SPLIT = f'{BASE}/fase3d2_output/split_v2.csv'
# kamus hasil run sebelum eksklusi (bila folder lama sudah di-rename) -> pembanding
F_KAMUS_PRA = f'{BASE}/fase1v2_output_pra_eksklusi/kamus_palembang_beku_v2.csv'
IN_K = f'{BASE}/input_kamus'
KAMUS_PLG = f'{IN_K}/kamus_palembang.csv'
KAMUS_CEK = f'{IN_K}/kamus_palembang_beku_cek.csv'
JENIS_TAMBAHAN = f'{IN_K}/jenis_tambahan.csv'
KAMUS_GAUL = f'{IN_K}/kamus_gaul_indo.csv'
URL_GAUL = 'https://raw.githubusercontent.com/nasalsabila/kamus-alay/master/colloquial-indonesian-lexicon.csv'
OUT = f'{BASE}/fase1v2_output'

os.makedirs(IN_K, exist_ok=True)
if not os.path.exists(KAMUS_GAUL):
    urllib.request.urlretrieve(URL_GAUL, KAMUS_GAUL)
    print('Kamus gaul diunduh ke', KAMUS_GAUL)
for f in [F_MASTER, F_LABEL, F_SPLIT, KAMUS_PLG, KAMUS_CEK, KAMUS_GAUL]:
    if not os.path.exists(f):
        raise SystemExit(f'File tidak ditemukan: {f}')
F_MASTER_V3 = f'{OUT}/master_dataset_v3.csv'
if os.path.exists(F_MASTER_V3):
    print('PERHATIAN: master_dataset_v3.csv sudah ada dan akan DITIMPA. Hasil deterministik; '
          'boleh dijalankan ulang HANYA untuk melengkapi kolom jenis, sebelum eksperimen dimulai.')
os.makedirs(OUT, exist_ok=True)

LOG = []
def log(msg=''):
    print(msg); LOG.append(str(msg))


# %% SEL 2 - Fungsi (disalin PERSIS dari Fase 0/1)
def text_cleaning(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\@\w+", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

negation_words = {"tidak", "bukan", "tak", "jangan", "tdk", "gak", "enggak", "dak", "idakk", "idk"}
custom_stopwords = {"di", "ke", "dari", "yang", "dan", "atau", "untuk", "pada", "dengan",
                    "adalah", "itu", "ini", "yg", "nya", "kalo", "ya", "aja"} - negation_words

k_indo = pd.read_csv(KAMUS_GAUL)
dict_indo = dict(zip(k_indo["slang"].astype(str), k_indo["formal"].astype(str)))
k_plg = pd.read_csv(KAMUS_PLG)
dict_plg_lama = dict(zip(k_plg["kata_gaul"].astype(str), k_plg["kata_baku"].astype(str)))

def tokens_setelah_gaul(text):
    return [dict_indo.get(w, w) for w in text_cleaning(text).split()]

def preprocess(text, dict_plg=None):
    toks = tokens_setelah_gaul(text)
    if dict_plg is not None:
        toks = [dict_plg.get(w, w) for w in toks]
    toks = [w for w in toks if w not in custom_stopwords and len(w) > 1]
    return " ".join(toks)

aspect_keywords = {   # leksikon aspek BEKU (tidak diubah)
    "Kebijakan & Pelaksanaan": ["wali", "pak", "admin", "warga", "masyarakat", "sehat", "lanjut",
                                "terus", "pemerintah", "program", "dukung", "setuju"],
    "Lokasi & Fasilitas": ["ampera", "jembatan", "hulu", "penuh", "ramai", "tempat", "fasilitas",
                           "parkir", "sampah", "bazar", "umkm", "jualan", "jual", "bersih", "kotor"],
    "Akses Lalu Lintas": ["jalan", "macet", "motor", "mobil", "tutup", "akses", "rute", "lintas",
                          "kendaraan", "lancar"],
}
def aspect_scores(text):
    words = str(text).split()
    return {a: sum(w in kw for w in words) for a, kw in aspect_keywords.items()}
def determine_aspect(text):
    sc = aspect_scores(text)
    best = max(sc, key=sc.get)
    return np.nan if sc[best] == 0 else best

KOREKSI = [   # koreksi manual pra-eksperimen (sama dengan Fase 1 v1)
    ("ktk", "ketika", "tidak ada", "singkatan 'katek'; konteks korpus bermakna 'tidak ada'"),
    ("nnyo", "nanti", "tanya", "singkatan 'nanyo'; konteks korpus bermakna 'bertanya'"),
]


# %% SEL 3 - Muat data & cek replikasi
m = pd.read_csv(F_MASTER, dtype=str, keep_default_na=False)
lab = pd.read_csv(F_LABEL, dtype=str, keep_default_na=False)
sp = pd.read_csv(F_SPLIT, dtype=str, keep_default_na=False)
assert len(m) == 4382, 'master_dataset_v2.csv harus 4.382 baris (sebelum eksklusi)'
N_KORPUS = len(sp)
assert len(lab) == N_KORPUS and set(lab.doc_id) == set(sp.doc_id) and set(sp.doc_id) <= set(m.doc_id)
m = m[m.doc_id.isin(sp.doc_id)].copy()
m = m.merge(sp[['doc_id', 'grup', 'split']], on='doc_id')
assert len(m) == N_KORPUS
assert m.split.isin(['latih', 'validasi', 'uji']).all()

log('=' * 70); log('FASE 1 v2 - PEMBEKUAN KAMUS PALEMBANG DARI DATA LATIH'); log('=' * 70)
log(f'{datetime.datetime.now():%Y-%m-%d %H:%M}')
log(f'Korpus setelah eksklusi tambahan (fase3d2): {N_KORPUS} komentar ({4382 - N_KORPUS} dikeluarkan)')
cek_s1 = (m.text.map(lambda t: preprocess(t, None)) == m.clean_text_s1).mean()
cek_s2_lama = (m.text.map(lambda t: preprocess(t, dict_plg_lama)) == m.clean_text_s2_lama).mean()
cek = pd.read_csv(KAMUS_CEK, dtype=str, keep_default_na=False)
dict_beku_v1 = dict(zip(cek.kata_gaul, cek.kata_baku))
for k, lama, baru, _ in KOREKSI:
    if k in dict_beku_v1:
        dict_beku_v1[k] = baru
cek_s2_v1 = (m.text.map(lambda t: preprocess(t, dict_beku_v1)) == m.clean_text_s2).mean()
log(f'Cek replikasi: S1 {cek_s1:.1%} | S2 kamus asli {cek_s2_lama:.1%} | S2 kamus beku v1 {cek_s2_v1:.1%}')
assert cek_s1 == 1.0 and cek_s2_lama == 1.0, 'Replikasi pra-pemrosesan tidak setia (kamus gaul/kamus asli berbeda?).'
assert cek_s2_v1 == 1.0, 'Kamus beku v1 hasil rekonstruksi tidak cocok dengan master (cek kamus_palembang_beku_cek.csv).'
log(f'Kamus beku v1 (pembanding): {len(dict_beku_v1)} entri')


# %% SEL 4 - Pembekuan dari data latih
latih = m[m.split == 'latih']
bukan_latih = m[m.split != 'latih']
uji = m[m.split == 'uji']
log(f'\nSumber pembekuan = data latih: {len(latih)} komentar '
    f'(validasi {int((m.split == "validasi").sum())}, uji {len(uji)} TIDAK dipakai)')

log(f'Kamus Palembang asli: {len(k_plg)} baris | {k_plg.kata_gaul.nunique()} kunci unik')
identitas = {k for k, v in dict_plg_lama.items() if k == v}
efektif = {k: v for k, v in dict_plg_lama.items() if k != v}
log(f'  entri identitas: {len(identitas)} | entri efektif: {len(efektif)}')

frek_latih = Counter(w for t in latih.text for w in tokens_setelah_gaul(t))
ndok_latih = Counter(w for t in latih.text for w in set(tokens_setelah_gaul(t)))
frek_latih_mentah = Counter(w for t in latih.text for w in text_cleaning(t).split())
frek_bukan = Counter(w for t in bukan_latih.text for w in tokens_setelah_gaul(t))
frek_uji = Counter(w for t in uji.text for w in tokens_setelah_gaul(t))

beku_keys = sorted(k for k in efektif if frek_latih[k] > 0)
dict_beku = {k: efektif[k] for k in beku_keys}
log(f'\nKOREKSI MANUAL PRA-EKSPERIMEN:')
for k, lama, baru, alasan in KOREKSI:
    if k in dict_beku:
        assert dict_beku[k] == lama, f'entri {k} tidak sesuai harapan'
        dict_beku[k] = baru
        log(f'  {k}: {lama} -> {baru} | {alasan}')
    else:
        log(f'  {k}: tidak masuk kamus beku (tidak muncul di data latih) -> koreksi tidak diperlukan')

terbuang = sorted(k for k in efektif if frek_bukan[k] > 0 and frek_latih[k] == 0)
tertimpa = sorted(k for k in efektif if frek_latih_mentah[k] > 0 and frek_latih[k] == 0)
log(f'\nKAMUS BEKU v2: {len(dict_beku)} entri (v1: {len(dict_beku_v1)})')
log(f'  frekuensi 1 di data latih: {sum(frek_latih[k] == 1 for k in beku_keys)}')
log(f'  TERBUANG (muncul di validasi/uji tetapi tidak di latih): {len(terbuang)}')
log(f'  tertimpa kamus gaul (muncul di teks mentah latih, diubah kamus gaul duluan): {len(tertimpa)}')
masuk = sorted(set(dict_beku) - set(dict_beku_v1))
keluar = sorted(set(dict_beku_v1) - set(dict_beku))
log(f'  dibanding v1: entri baru {len(masuk)} | entri hilang {len(keluar)}')
log(f'    baru  : {masuk[:40]}')
log(f'    hilang: {keluar[:40]}')
if os.path.exists(F_KAMUS_PRA):
    pra = pd.read_csv(F_KAMUS_PRA, dtype=str, keep_default_na=False)
    d_pra = dict(zip(pra.kata_gaul, pra.kata_baku))
    hilang_eks = sorted(set(d_pra) - set(dict_beku))
    baru_eks = sorted(set(dict_beku) - set(d_pra))
    beda_isi = sorted(k for k in set(d_pra) & set(dict_beku) if d_pra[k] != dict_beku[k])
    log(f'  dibanding kamus SEBELUM eksklusi ({len(d_pra)} entri): hilang {len(hilang_eks)} {hilang_eks} | '
        f'baru {len(baru_eks)} {baru_eks} | isi berbeda {len(beda_isi)}')
else:
    log('  (pembanding kamus sebelum eksklusi tidak ditemukan; rename folder lama menjadi fase1v2_output_pra_eksklusi)')

tok_penuh = sum(frek_uji[k] for k in efektif)
tok_beku = sum(frek_uji[k] for k in dict_beku)
dok_penuh = uji.text.map(lambda t: any(w in efektif for w in tokens_setelah_gaul(t))).sum()
dok_beku = uji.text.map(lambda t: any(w in dict_beku for w in tokens_setelah_gaul(t))).sum()
log(f'\nCAKUPAN PADA DATA UJI (seandainya kamus asli penuh vs kamus beku v2)')
log(f'  token ternormalisasi: kamus asli {tok_penuh} | kamus beku {tok_beku} '
    f'({tok_beku / tok_penuh:.1%})' if tok_penuh else '  token: -')
log(f'  dokumen tersentuh   : kamus asli {dok_penuh} | kamus beku {dok_beku} (dari {len(uji)})')


# %% SEL 5 - Kolom jenis & simpan kamus
peta_jenis = dict(zip(cek.kata_gaul, cek.jenis))
if os.path.exists(JENIS_TAMBAHAN):
    jt = pd.read_csv(JENIS_TAMBAHAN, dtype=str, keep_default_na=False)
    assert {'kata_gaul', 'jenis'} <= set(jt.columns), 'jenis_tambahan.csv harus berkolom kata_gaul,jenis'
    peta_jenis.update({k: v for k, v in zip(jt.kata_gaul, jt.jenis) if v.strip()})
    log(f'\njenis_tambahan.csv dibaca: {len(jt)} baris')
kb = pd.DataFrame({'kata_gaul': beku_keys, 'kata_baku': [dict_beku[k] for k in beku_keys],
                   'frek_latih': [frek_latih[k] for k in beku_keys],
                   'n_dok_latih': [ndok_latih[k] for k in beku_keys],
                   'frek_uji': [frek_uji[k] for k in beku_keys]})
kb['jenis'] = kb.kata_gaul.map(peta_jenis).fillna('')
kb['dikoreksi'] = kb.kata_gaul.isin([k for k, *_ in KOREKSI])
kb = kb.sort_values('frek_latih', ascending=False)
kb.to_csv(f'{OUT}/kamus_palembang_beku_v2.csv', index=False)
tanpa = kb[kb.jenis == ''][['kata_gaul', 'kata_baku', 'frek_latih']].assign(jenis='')
tanpa.to_csv(f'{OUT}/entri_tanpa_jenis.csv', index=False)
log(f'\nKolom jenis terisi {(kb.jenis != "").sum()}/{len(kb)}; tanpa jenis: {len(tanpa)} '
    '-> isi di entri_tanpa_jenis.csv (dialek / informal umum / singkatan / pemanjangan), '
    'simpan sebagai input_kamus/jenis_tambahan.csv, lalu jalankan ulang skrip ini.')
if (kb.jenis != '').any():
    komp = kb[kb.jenis != ''].groupby('jenis').agg(n_entri=('kata_gaul', 'size'), kemunculan_latih=('frek_latih', 'sum'))
    komp['%entri'] = (komp.n_entri / komp.n_entri.sum() * 100).round(1)
    komp['%kemunculan'] = (komp.kemunculan_latih / komp.kemunculan_latih.sum() * 100).round(1)
    log('KOMPOSISI KAMUS BEKU v2 (entri berjenis):\n' + komp.sort_values('n_entri', ascending=False).to_string())

pd.DataFrame({'kata_gaul': sorted(set(dict_beku) | set(dict_beku_v1))}).assign(
    di_v1=lambda x: x.kata_gaul.isin(dict_beku_v1), di_v2=lambda x: x.kata_gaul.isin(dict_beku)).to_csv(
    f'{OUT}/perbandingan_kamus_v1_v2.csv', index=False)
pd.DataFrame({'kata_gaul': terbuang, 'kata_baku': [efektif[k] for k in terbuang],
              'frek_validasi_uji': [frek_bukan[k] for k in terbuang]}).to_csv(f'{OUT}/entri_terbuang.csv', index=False)
pd.DataFrame({'kata_gaul': tertimpa, 'kata_baku_plg': [efektif[k] for k in tertimpa],
              'diubah_kamus_gaul_jadi': [dict_indo.get(k, k) for k in tertimpa]}).to_csv(
    f'{OUT}/entri_tertimpa_gaul.csv', index=False)


# %% SEL 6 - Hitung ulang S2, aspek, gabung label & split -> master_dataset_v3.csv
m['clean_text_s2_v1'] = m['clean_text_s2']
m['clean_text_s2'] = m.text.map(lambda t: preprocess(t, dict_beku))
sc = m.clean_text_s2.map(aspect_scores)
m['Aspek'] = m.clean_text_s2.map(determine_aspect)
m['n_aspek_cocok'] = sc.map(lambda s: sum(v > 0 for v in s.values()))
m['seri'] = sc.map(lambda s: sorted(s.values())[-1] > 0 and sorted(s.values())[-1] == sorted(s.values())[-2])
m = m.merge(lab[['doc_id', 'label', 'label_kode', 'sumber_label']], on='doc_id')

log(f'\nS2 berubah dibanding kamus beku v1: {(m.clean_text_s2 != m.clean_text_s2_v1).sum()} dari {len(m)}')
log(f'S1 kosong: {(m.clean_text_s1.str.strip() == "").sum()} | S2 kosong: {(m.clean_text_s2.str.strip() == "").sum()} '
    '(korpus tidak dipangkas; dilaporkan)')
log(f'Komentar tersentuh kamus (S1 != S2): {(m.clean_text_s1 != m.clean_text_s2).sum()}')
log('\nPER SPLIT:')
for s in ['latih', 'validasi', 'uji']:
    x = m[m.split == s]
    log(f'  {s:9s}: n {len(x)} | terpetakan aspek {x.Aspek.notna().sum()} ({x.Aspek.notna().mean():.1%}) | '
        f'tersentuh kamus {(x.clean_text_s1 != x.clean_text_s2).mean():.1%}')
log('\nLABEL x ASPEK (seluruh korpus, label manusia):')
log(pd.crosstab(m.Aspek.fillna('TAK TERPETAKAN'), m.label).to_string())
log(f'multi-aspek: {(m.n_aspek_cocok > 1).sum()} | seri: {int(m.seri.sum())}')

kol = ['doc_id', 'platform', 'run', 'post_id', 'grup', 'split', 'author_hash', 'created_at', 'text', 'text_clean',
       'clean_text_s1', 'clean_text_s2', 'clean_text_s2_v1', 'label', 'label_kode', 'sumber_label',
       'Aspek', 'n_aspek_cocok', 'seri']
m[kol].to_csv(F_MASTER_V3, index=False)


# %% SEL 7 - Simpan audit
with open(f'{OUT}/audit_fase1v2.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(LOG) + '\n')
print(f'\nSelesai. Keluaran di {OUT}/ ; master_dataset_v3.csv dipakai Fase 2 dan Fase 3.')
