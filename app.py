import re
import streamlit as st

st.set_page_config(page_title="BioQuizBot", layout="centered")
st.title("🧬 BioQuizBot — Pembuat Soal Biologi")
st.caption("Chatbot ini hanya membuat soal Biologi. Topik selain Biologi akan ditolak.")

# --- Daftar kata kunci biologi (boleh kamu tambah) ---
BIO_KEYWORDS = [
    "biologi", "sel", "jaringan", "organ", "sistem organ", "dna", "rna", "gen",
    "genetika", "mutasi", "evolusi", "ekologi", "populasi", "komunitas", "bioma",
    "fotosintesis", "respirasi", "enzim", "metabolisme", "mitosis", "meiosis",
    "virus", "bakteri", "protista", "jamur", "tumbuhan", "hewan", "manusia",
    "anatomi", "fisiologi", "imunitas", "hormon", "reproduksi", "pencernaan",
    "peredaran darah", "pernapasan", "saraf", "homeostasis", "mikrobiologi"
]

# Kata kunci yang sering menandakan non-biologi
NON_BIO_HINTS = [
    "matematika", "fisika", "kimia", "sejarah", "geografi", "ekonomi",
    "sosiologi", "bahasa", "inggris", "pemrograman", "coding", "javascript",
    "python", "agama", "ppkn"
]

def is_biology_request(text: str) -> bool:
    t = text.lower()
    # kalau ada tanda non-biologi yang kuat, tolak
    if any(k in t for k in NON_BIO_HINTS) and not ("biologi" in t):
        return False
    # lolos jika ada kata kunci biologi
    return any(k in t for k in BIO_KEYWORDS)

def generate_biology_questions(topic: str, level: str, n: int, qtype: str):
    # Generator sederhana (tanpa LLM): template + variasi.
    # Kalau kamu pakai LLM nanti, fungsi ini tinggal diganti.
    questions = []
    topic_clean = topic.strip()

    for i in range(1, n + 1):
        if qtype == "Pilihan Ganda":
            q = (
                f"{i}. ({level}) Topik: {topic_clean}\n"
                f"Pertanyaan: Apa pernyataan yang paling tepat terkait {topic_clean}?\n"
                f"A. Definisi yang tidak sesuai\n"
                f"B. Penjelasan yang benar dan relevan\n"
                f"C. Contoh yang tidak terkait\n"
                f"D. Kesimpulan yang keliru\n"
                f"Jawaban: B\n"
                f"Pembahasan singkat: {topic_clean} berkaitan dengan konsep/struktur/proses biologis yang dapat dijelaskan secara ilmiah.\n"
            )
        elif qtype == "Isian Singkat":
            q = (
                f"{i}. ({level}) Topik: {topic_clean}\n"
                f"Pertanyaan: Jelaskan secara singkat apa yang dimaksud dengan {topic_clean}.\n"
                f"Jawaban: (Isi jawaban ringkas, 1–2 kalimat)\n"
            )
        else:  # Essay
            q = (
                f"{i}. ({level}) Topik: {topic_clean}\n"
                f"Pertanyaan: Uraikan mekanisme/konsep {topic_clean} beserta contoh penerapannya dalam kehidupan.\n"
                f"Rubrik: Ketepatan konsep, kelengkapan penjelasan, contoh relevan.\n"
            )
        questions.append(q)

    return "\n".join(questions)

# ---- UI ----
with st.sidebar:
    st.header("⚙️ Pengaturan Soal")
    level = st.selectbox("Tingkat", ["SMP", "SMA", "Kuliah"])
    qtype = st.selectbox("Tipe soal", ["Pilihan Ganda", "Isian Singkat", "Essay"])
    n = st.slider("Jumlah soal", 1, 20, 5)

st.subheader("💬 Chat")
if "messages" not in st.session_state:
    st.session_state.messages = []

# tampilkan riwayat
for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

user_msg = st.chat_input("Contoh: 'Buat 5 soal tentang fotosintesis kelas SMA'")

if user_msg:
    st.session_state.messages.append(("user", user_msg))
    with st.chat_message("user"):
        st.markdown(user_msg)

    # Guardrail: cek harus biologi
    if not is_biology_request(user_msg):
        bot_reply = (
            "❌ Maaf, aku hanya bisa membuat soal **Biologi**.\n\n"
            "Coba tulis permintaan seperti:\n"
            "- 'Buat 10 soal pilihan ganda tentang sistem pernapasan manusia'\n"
            "- 'Buat 5 soal tentang mitosis dan meiosis untuk SMA'\n"
        )
    else:
        # Ambil topik dari kalimat: cari "tentang ..."
        m = re.search(r"tentang (.+)", user_msg.lower())
        topic = m.group(1).strip() if m else "Biologi (umum)"

        bot_reply = (
            f"✅ Oke! Ini {n} soal {qtype} Biologi tingkat {level} tentang **{topic}**:\n\n"
            + generate_biology_questions(topic, level, n, qtype)
        )

    st.session_state.messages.append(("assistant", bot_reply))
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
