import io
import numpy as np
import streamlit as st
from scipy import signal
from scipy.io import wavfile
import time

st.title("🔇 Ultrasonic Jammer - Versión Realista")

if st.button("🚀 ACTIVAR JAMMER", type="primary", use_container_width=True):
    st.success("Jammer activado - Probando rango detectable")
    
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            fs = 96000
            duration = 20
            n_samples = int(duration * fs)
            
            # Rango más bajo (más probable que funcione)
            lowcut = 16500
            highcut = 20500
            
            audio = np.random.randn(n_samples).astype(np.float64) * 2.8
            
            b, a = signal.butter(5, [lowcut, highcut], btype='bandpass', fs=fs)
            jammer = signal.filtfilt(b, a, audio)
            
            jammer *= 2.4
            jammer = jammer / np.max(np.abs(jammer)) * 0.9
            
            audio_int16 = np.int16(jammer * 32767)
            buffer = io.BytesIO()
            wavfile.write(buffer, fs, audio_int16)
            buffer.seek(0)
            
            st.audio(buffer, format="audio/wav", autoplay=True)
            
            st.info(f"Reproduciendo: **{lowcut}-{highcut} Hz**")
            st.warning("Si sigues sin escuchar nada, es porque tus bocinas no llegan a estas frecuencias.")
            
        time.sleep(duration - 3)
