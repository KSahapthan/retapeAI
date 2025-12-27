# eda.py
from pathlib import Path
import wave

# base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

# list all WAV files in the data folder
wav_files = sorted(DATA_DIR.glob("*.wav"))

if not wav_files:
    print("No WAV files found in", DATA_DIR)
    exit()

# loop over each file and print metadata
for audio_path in wav_files:
    with wave.open(str(audio_path), "rb") as wf:
        print(f"\nFile: {audio_path.name}")
        print("Channels:", wf.getnchannels())
        print("Sample rate:", wf.getframerate())
        print("Sample width:", wf.getsampwidth())
        print("Frames:", wf.getnframes())
