import streamlit as st
import numpy as np
from scipy import signal
from scipy.io import wavfile
import io

st.set_page_config(page_title="Jammer Básico", page_icon="🔊", layout="centered")
st.title("🎤 Generador de Jammer Básico")
st.markdown("**Interferencia para grabaciones no autorizadas**")

# --- Parámetros ---
col1, col2 = st.columns(2)

with col1:
    duration = st.slider("Duración (segundos)", 5, 120, 30, step=5)
    intensity = st.slider("Intensidad del Jammer", 0.8, 2.2, 1.6, step=0.1)

with col2:
    seed = st.number_input("Semilla (para reproducibilidad)", value=42, step=1)
    fs = 44100

if st.button("🚀 Generar Jammer", type="primary"):
    with st.spinner("Generando audio..."):
        # --- Generación del audio ---
        n_samples = int(duration * fs)
        np.random.seed(seed)
        
        white = np.random.randn(n_samples)
        noise = np.cumsum(white, dtype=np.float64)
        noise -= np.mean(noise)
        noise /= np.std(noise)
        
        # Filtros
        b1, a1 = signal.butter(2, [200, 6500], btype='bandpass', fs=fs)
        b2, a2 = signal.butter(3, [800, 4000], btype='bandpass', fs=fs)
        
        zi1 = signal.lfilter_zi(b1, a1) * noise[0]
        zi2 = signal.lfilter_zi(b2, a2) * noise[0]
        
        filtered1, _ = signal.lfilter(b1, a1, noise, zi=zi1)
        filtered2, _ = signal.lfilter(b2, a2, noise, zi=zi2)
        
        jammer = 0.45 * noise + 0.55 * filtered1 + 0.35 * filtered2
        jammer *= intensity
        
        # Normalizar
        peak = np.max(np.abs(jammer))
        jammer = (jammer / peak) * 0.95
        
        # Fade
        fade = int(0.08 * fs)
        envelope = np.ones(n_samples)
        envelope[:fade] = np.linspace(0, 1, fade)
        envelope[-fade:] = np.linspace(1, 0, fade)
        jammer *= envelope
        
        # Convertir a bytes
        audio_int16 = np.int16(jammer * 32767)
        
        # Guardar en memoria
        buffer = io.BytesIO()
        wavfile.write(buffer, fs, audio_int16)
        buffer.seek(0)
        
        st.success("¡Jammer generado correctamente!")
        
        # Reproducir audio
        st.audio(buffer, format="audio/wav")
        
        # Descargar
        st.download_button(
            label="⬇️ Descargar archivo WAV",
            data=buffer,
            file_name=f"jammer_{duration}s_intensity{intensity:.1f}.wav",
            mime="audio/wav"
        )

st.info("**Recomendación:** Usa altavoces potentes y colócalos cerca del micrófono objetivo.")
st.warning("⚠️ Este tipo de herramientas deben usarse solo para protección de privacidad en espacios propios. Revisa las leyes de tu país.")
