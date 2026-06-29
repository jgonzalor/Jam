import io
import numpy as np
import streamlit as st
from scipy import signal
from scipy.io import wavfile

st.set_page_config(page_title="Jammer Ultrasónico", page_icon="🔇", layout="centered")

st.title("🔇 Jammer Ultrasónico (Casi Inaudible)")
st.markdown("**Diseñado para interferir micrófonos sin molestar mucho al oído humano**")

st.warning("⚠️ Requiere **buenos altavoces** con respuesta en agudos altos. En altavoces normales perderá efectividad.")

col1, col2 = st.columns(2)

with col1:
    duration = st.slider("Duración (segundos)", 10, 300, 60, step=10)
    intensity = st.slider("Intensidad", 0.8, 2.8, 2.0, step=0.1)

with col2:
    fs = st.selectbox("Frecuencia de muestreo", [44100, 48000, 96000], index=2)  # Mejor usar 96kHz
    seed = st.number_input("Semilla", value=123, step=1)

# Rango ultrasónico
lowcut = st.slider("Frecuencia mínima (Hz)", 16000, 21000, 18500, step=100)
highcut = st.slider("Frecuencia máxima (Hz)", 20000, 24000, 22500, step=100)

fade_ms = st.slider("Fade In/Out (ms)", 100, 1000, 300)

if st.button("Generar Jammer Ultrasónico", type="primary"):
    with st.spinner("Generando señal ultrasónica..."):
        n_samples = int(duration * fs)
        np.random.seed(seed)

        # Ruido blanco (mejor para ultrasonido)
        audio = np.random.randn(n_samples).astype(np.float64)
        
        # Filtro bandpass en rango ultrasónico
        b, a = signal.butter(4, [lowcut, highcut], btype='bandpass', fs=fs)
        jammer = signal.filtfilt(b, a, audio)

        # Aumentar intensidad
        jammer *= intensity
        
        # Normalizar
        jammer = jammer / np.max(np.abs(jammer)) * 0.92

        # Fade
        fade_samples = int(fade_ms * fs / 1000)
        envelope = np.ones(n_samples)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        jammer *= envelope

        # Exportar
        audio_int16 = np.int16(jammer * 32767)
        buffer = io.BytesIO()
        wavfile.write(buffer, fs, audio_int16)
        buffer.seek(0)

        st.success("Jammer Ultrasónico generado")
        st.audio(buffer, format="audio/wav")

        st.download_button(
            label="⬇️ Descargar WAV",
            data=buffer.getvalue(),
            file_name=f"jammer_ultrasonico_{lowcut}-{highcut}Hz_{duration}s.wav",
            mime="audio/wav"
        )

        st.info("Prueba con volumen alto y altavoces de buena calidad.")
