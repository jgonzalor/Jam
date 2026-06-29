import io
import numpy as np
import streamlit as st
from scipy import signal
from scipy.io import wavfile
import time

st.set_page_config(page_title="Ultrasónico Jammer", page_icon="🔇", layout="centered")

st.title("🔇 ULTRASONIC JAMMER")
st.markdown("**Presiona el botón para activar el jammer ultrasónico**")

# Configuración fija (optimizada)
duration = 30          # segundos por archivo
fs = 96000             # Sample rate alto (importante)
lowcut = 19200
highcut = 23500
intensity = 2.6

# Botón grande
if st.button("🚀 ACTIVAR JAMMER ULTRASÓNICO", type="primary", use_container_width=True):
    st.success("Jammer Ultrasónico Activado - Reproduciendo en bucle")
    
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            try:
                n_samples = int(duration * fs)
                seed = int(time.time())  # Semilla cambia para que no sea repetitivo
                
                # Generar ruido ultrasónico
                audio = np.random.randn(n_samples).astype(np.float64) * 3.0
                
                b, a = signal.butter(6, [lowcut, highcut], btype='bandpass', fs=fs)
                jammer = signal.filtfilt(b, a, audio)
                
                jammer *= intensity
                jammer = jammer / np.max(np.abs(jammer)) * 0.88
                
                # Fade corto
                fade = int(0.15 * fs)
                envelope = np.ones(n_samples)
                envelope[:fade] = np.linspace(0, 1, fade)
                envelope[-fade:] = np.linspace(1, 0, fade)
                jammer *= envelope
                
                # Convertir a WAV
                audio_int16 = np.int16(jammer * 32767)
                buffer = io.BytesIO()
                wavfile.write(buffer, fs, audio_int16)
                buffer.seek(0)
                
                st.audio(buffer, format="audio/wav", autoplay=True)
                
                st.info(f"Reproduciendo jammer ultrasónico ({lowcut}-{highcut} Hz)")
                st.caption("Presiona Stop en el reproductor o refresca la página para detener.")
                
            except:
                st.error("Error en reproducción. Intenta de nuevo.")
            
        time.sleep(duration - 2)  # Espera casi toda la duración para loop continuo
