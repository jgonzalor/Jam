import io
import numpy as np
import streamlit as st
from scipy import signal
from scipy.io import wavfile

st.set_page_config(page_title="Jammer Audible Fuerte", page_icon="🔊", layout="centered")

st.title("🔊 Jammer Audible Fuerte")
st.markdown("**Optimizado para bocinas USB normales**")

st.warning("Este audio es **fuerte y molesto**. Úsalo con responsabilidad.")

# ===================== CONTROLES =====================
col1, col2 = st.columns(2)

with col1:
    duration = st.slider("Duración (segundos)", 10, 300, 60, step=5)
    intensity = st.slider("Intensidad (Fuerza)", 1.0, 2.8, 2.0, step=0.1)

with col2:
    fs = st.selectbox("Calidad de audio", [44100, 48000], index=0)
    seed = st.number_input("Semilla", value=42, step=1)

# Rango optimizado para micrófonos de celular
st.subheader("Rango de Frecuencias")
colf1, colf2 = st.columns(2)
with colf1:
    lowcut = st.slider("Frecuencia mínima (Hz)", 100, 800, 180, step=10)
with colf2:
    highcut = st.slider("Frecuencia máxima (Hz)", 3000, 8500, 6200, step=50)

fade_ms = st.slider("Fade In/Out (ms)", 50, 500, 120, step=20)

# ===================== FUNCIÓN PRINCIPAL =====================
def generar_jammer_fuerte():
    n_samples = int(duration * fs)
    np.random.seed(seed)

    # Ruido base marrón (más denso)
    white = np.random.randn(n_samples)
    audio = np.cumsum(white).astype(np.float64)
    audio -= np.mean(audio)
    audio /= np.std(audio)

    # Filtros fuertes para saturar micrófonos
    b1, a1 = signal.butter(3, [lowcut, highcut], btype='bandpass', fs=fs)
    b2, a2 = signal.butter(4, [900, 4800], btype='bandpass', fs=fs)   # Zona crítica

    filtered1 = signal.filtfilt(b1, a1, audio)
    filtered2 = signal.filtfilt(b2, a2, audio)

    # Mezcla agresiva
    jammer = 0.3 * audio + 0.45 * filtered1 + 0.55 * filtered2
    jammer = jammer * intensity

    # Normalizar fuerte
    jammer = jammer / np.max(np.abs(jammer)) * 0.94

    # Fade rápido
    fade_samples = int(fade_ms * fs / 1000)
    if fade_samples * 2 < n_samples:
        envelope = np.ones(n_samples)
        envelope[:fade_samples] = np.linspace(0.0, 1.0, fade_samples)
        envelope[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)
        jammer *= envelope

    # Convertir a WAV
    audio_int16 = np.int16(jammer * 32767)
    buffer = io.BytesIO()
    wavfile.write(buffer, fs, audio_int16)
    buffer.seek(0)

    return buffer

# ===================== BOTÓN =====================
if st.button("🔊 GENERAR JAMMER FUERTE", type="primary", use_container_width=True):
    with st.spinner("Generando audio fuerte..."):
        buffer = generar_jammer_fuerte()

    st.success("✅ Audio generado correctamente")

    st.audio(buffer, format="audio/wav")

    st.download_button(
        label="⬇️ Descargar archivo WAV",
        data=buffer.getvalue(),
        file_name=f"jammer_fuerte_{duration}s.wav",
        mime="audio/wav"
    )

    st.info("**Instrucciones de uso:**\n"
            "• Conecta tus bocinas USB\n"
            "• Sube el volumen al **máximo**\n"
            "• Colócalas lo más cerca posible del celular / grabadora")

st.caption("Versión audible fuerte optimizada para micrófonos de celulares")
