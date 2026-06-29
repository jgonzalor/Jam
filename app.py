import io
import numpy as np
import streamlit as st
from scipy import signal
from scipy.io import wavfile


# ============================================================
# APP STREAMLIT - RUIDO DE ENMASCARAMIENTO AMBIENTAL
# Archivo principal recomendado: app.py
# ============================================================

st.set_page_config(
    page_title="Privacidad Ambiental",
    page_icon="🔊",
    layout="centered"
)


def generar_ruido_base(tipo_ruido: str, n_samples: int, seed: int | None = None):
    rng = np.random.default_rng(seed)

    if tipo_ruido == "Blanco":
        audio = rng.normal(0, 1, n_samples)

    elif tipo_ruido == "Marrón":
        white = rng.normal(0, 1, n_samples)
        audio = np.cumsum(white)

    else:
        # Ruido rosa aproximado
        white = rng.normal(0, 1, n_samples)
        b, a = signal.butter(1, 0.08, btype="lowpass")
        audio = signal.lfilter(b, a, white)

    return audio


def aplicar_filtro(audio, fs, lowcut, highcut):
    nyquist = fs / 2

    lowcut = max(20, float(lowcut))
    highcut = min(float(highcut), nyquist - 100)

    if lowcut >= highcut:
        return audio

    b, a = signal.butter(
        3,
        [lowcut, highcut],
        btype="bandpass",
        fs=fs
    )

    return signal.filtfilt(b, a, audio)


def normalizar_audio(audio, volumen):
    audio = audio.astype(np.float64)
    audio -= np.mean(audio)

    peak = np.max(np.abs(audio))

    if peak > 0:
        audio = audio / peak

    volumen = min(max(float(volumen), 0.05), 0.95)
    audio = audio * volumen

    return audio


def aplicar_fade(audio, fs, fade_ms):
    n_samples = len(audio)
    fade_samples = int((fade_ms / 1000) * fs)
    fade_samples = min(fade_samples, n_samples // 2)

    if fade_samples <= 0:
        return audio

    envelope = np.ones(n_samples)
    envelope[:fade_samples] = np.linspace(0.0, 1.0, fade_samples)
    envelope[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)

    return audio * envelope


def generar_audio_enmascaramiento(
    duration,
    fs,
    tipo_ruido,
    volumen,
    lowcut,
    highcut,
    fade_ms,
    seed
):
    n_samples = int(duration * fs)

    audio = generar_ruido_base(
        tipo_ruido=tipo_ruido,
        n_samples=n_samples,
        seed=seed
    )

    audio = aplicar_filtro(audio, fs, lowcut, highcut)
    audio = normalizar_audio(audio, volumen)
    audio = aplicar_fade(audio, fs, fade_ms)

    audio_int16 = np.int16(audio * 32767)

    buffer = io.BytesIO()
    wavfile.write(buffer, fs, audio_int16)
    buffer.seek(0)

    return audio, buffer


def nombre_archivo(tipo_ruido, duration):
    tipo = tipo_ruido.lower().replace("ó", "o")
    return f"ruido_enmascaramiento_{tipo}_{duration}s.wav"


# ============================================================
# INTERFAZ
# ============================================================

st.title("🔊 Generador de Ruido de Enmascaramiento Ambiental")

st.markdown(
    """
Herramienta para generar audio audible de fondo orientado a **privacidad ambiental**
en reuniones, oficinas o espacios propios/autorizados.
"""
)

st.warning(
    "Esta app no bloquea micrófonos, no garantiza impedir grabaciones y no utiliza ultrasonido. "
    "Su función es generar ruido audible de fondo para reducir la claridad de conversaciones en el ambiente."
)

col1, col2 = st.columns(2)

with col1:
    duration = st.slider(
        "Duración del audio",
        min_value=5,
        max_value=600,
        value=60,
        step=5,
        help="Duración en segundos."
    )

    tipo_ruido = st.selectbox(
        "Tipo de ruido",
        options=["Rosa", "Blanco", "Marrón"],
        index=0,
        help="El ruido rosa suele ser más cómodo para uso prolongado."
    )

    volumen = st.slider(
        "Volumen interno del archivo",
        min_value=0.10,
        max_value=0.95,
        value=0.65,
        step=0.05
    )

with col2:
    fs = st.selectbox(
        "Frecuencia de muestreo",
        options=[22050, 44100, 48000],
        index=1
    )

    lowcut = st.slider(
        "Frecuencia mínima Hz",
        min_value=20,
        max_value=1000,
        value=250,
        step=10
    )

    highcut = st.slider(
        "Frecuencia máxima Hz",
        min_value=1000,
        max_value=10000,
        value=4500,
        step=100
    )

    fade_ms = st.slider(
        "Fade in/out ms",
        min_value=50,
        max_value=2000,
        value=300,
        step=50
    )

seed_enabled = st.checkbox("Usar semilla fija", value=True)

if seed_enabled:
    seed = st.number_input(
        "Semilla",
        min_value=0,
        max_value=999999,
        value=42,
        step=1
    )
else:
    seed = None


if st.button("🎧 Generar audio", type="primary"):
    if lowcut >= highcut:
        st.error("La frecuencia mínima debe ser menor que la frecuencia máxima.")
    else:
        with st.spinner("Generando audio..."):
            audio, buffer = generar_audio_enmascaramiento(
                duration=duration,
                fs=fs,
                tipo_ruido=tipo_ruido,
                volumen=volumen,
                lowcut=lowcut,
                highcut=highcut,
                fade_ms=fade_ms,
                seed=seed
            )

            wav_bytes = buffer.getvalue()

        st.success("Audio generado correctamente.")

        st.audio(wav_bytes, format="audio/wav")

        st.download_button(
            label="⬇️ Descargar archivo WAV",
            data=wav_bytes,
            file_name=nombre_archivo(tipo_ruido, duration),
            mime="
