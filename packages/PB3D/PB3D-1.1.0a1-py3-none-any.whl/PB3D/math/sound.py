import wave
import numpy as np

class SoundReader:
    def __init__(self, filename):
        self.filename = filename

    def read_wave(self):
        with wave.open(self.filename, 'r') as wave_file:
            frames = wave_file.readframes(-1)
            wave_data = np.frombuffer(frames, dtype=np.int16)
            return wave_data / 32767.0

