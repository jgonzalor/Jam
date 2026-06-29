import numpy as np
from scipy import signal
from scipy.io import wavfile

def generate_basic_jammer(duration=10.0, 
                         fs=44100, 
                         filename="jammer_basico.wav", 
                         seed=None,
                         intensity=1.0):
    """
    Jammer básico optimizado para saturar micrófonos
    """
    if seed is not None:
        np.random.seed(seed)
    
    n_samples = int(duration * fs)
    
    # Ruido base
    white = np.random.randn(n_samples)
    noise = np.cumsum(white, dtype=np.float64)
    noise -= np.mean(noise)
    noise /= np.std(noise)
    
    # === FILTROS PARA JAMMER ===
    # Banda principal de voz + frecuencias sensibles de micrófonos
    b1, a1 = signal.butter(2, [200, 6500], btype='bandpass', fs=fs)   # Banda ancha
    b2, a2 = signal.butter(3, [800, 4000], btype='bandpass', fs=fs)   # Zona más crítica
    
    # Inicializar estados
    zi1 = signal.lfilter_zi(b1, a1) * noise[0]
    zi2 = signal.lfilter_zi(b2, a2) * noise[0]
    
    filtered1, _ = signal.lfilter(b1, a1, noise, zi=zi1)
    filtered2, _ = signal.lfilter(b2, a2, noise, zi=zi2)
    
    # Mezcla agresiva (más peso en la zona crítica)
    jammer = (0.45 * noise + 
              0.55 * filtered1 + 
              0.35 * filtered2)
    
    # === INTENSIDAD ===
    jammer *= intensity   # Puedes subir hasta 1.8~2.0 con cuidado
    
    # Normalizar con headroom
    peak = np.max(np.abs(jammer))
    jammer = (jammer / peak) * 0.95
    
    # Fade in/out más rápido (para que empiece fuerte)
    fade_samples = int(0.08 * fs)   # 80ms
    
    fade_in = np.linspace(0.0, 1.0, fade_samples)
    fade_out = np.linspace(1.0, 0.0, fade_samples)
    
    envelope = np.ones(n_samples)
    envelope[:fade_samples] = fade_in
    envelope[-fade_samples:] = fade_out
    jammer *= envelope
    
    # Exportar
    audio_int16 = np.int16(jammer * 32767)
    wavfile.write(filename, fs, audio_int16)
    
    print(f"✅ Jammer básico generado: {filename}")
    print(f"   Duración: {duration}s | Intensidad: {intensity:.1f}x")
    
    return jammer, fs


# ===================== USO RECOMENDADO =====================
if __name__ == "__main__":
    generate_basic_jammer(
        duration=30,                    # Duración en segundos
        filename="jammer_30s.wav",
        intensity=1.6,                  # 1.0 = normal | 1.8 = muy agresivo
        seed=123
    )
