import io
import numpy as np
import streamlit as st
from scipy import signal
from scipy.io import wavfile

st.set_page_config(page_title="Jammer Ultrasónico", page_icon="🔇", layout="centered")

st.title("🔇 Jammer Ultrasónico (Inaudible)")
st.markdown("**Intento máximo de ruido inaudible para micrófonos**")

st.error("⚠️ Esta versión solo funciona bien con transductores o bocinas de muy buenos tweeters. Con bocinas USB normales la efectividad es baja.")

col1, col2 = st.columns(2)

with col1:
    duration = st.slider("Duración (segundos)", 10, 180, 45, step=5)
    intensity = st.slider("Intensidad", 1.5, 4.0, 2.8, step=0.1)

with col2:
    fs = st.selectbox("Sample Rate", [96000, 192000], index=0)  # Muy importante usar alto
    seed = st.number_input("Semilla", value=42)

lowcut = st.slider("Frecuencia mínima (Hz)", 17000, 22000, 19500, step=100)
highcut = st.slider("Frecuencia máxima (Hz)", 21000, 25000, 23500, step=100)

if st.button("Generar Jammer Ultrasónico", type="primary"):
    with st.spinner("Generando señal..."):
        n_samples = int(duration * fs)
        np.random.seed(seed)

        # Ruido blanco fuerte
        audio = np.random.randn(n_samples).astype(np.float64) * 3.0

        # Filtro muy agresivo en ultrasónico
        b, a = signal.butter(6, [lowcut, highcut], btype='bandpass', fs=fs)
        jammer = signal.filtfilt(b, a, audio)

        jammer *= intensity
        
        # Normalizar con mucho headroom
        max_val = np.max(np.abs(jammer))
        jammer = jammer / max_val * 0.85

        # Fade
        fade = int(0.2 * fs)
        envelope = np.ones(n_samples)
        envelope[:fade] = np.linspace(0, 1, fade)
        envelope[-fade:] = np.linspace(1, 0, fade)
        jammer *= envelope

        audio_int16 = np.int16(jammer * 32767)

        buffer = io.BytesIO()
        wavfile.write(buffer, fs, audio_int16)
        buffer.seek(0)

        st.success("Archivo generado")
        st.audio(buffer, format="audio/wav")

        st.download_button(
            "⬇️ Descargar WAV",
            data=buffer.getvalue(),
            file_name=f"ultrasonic_jammer_{lowcut}-{highcut}Hz_{duration}s.wav",
            mime="audio/wav"
        )

st.info("**Para mejores resultados:** Usa sample rate de 96kHz o 192kHz y prueba con volumen máximo.")
