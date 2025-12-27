# test.py
from pathlib import Path
import sys

# add project root to sys.path so we can import utils
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils.streaming import stream_wav

# path to the audio file
DATA_DIR = BASE_DIR / "data"
audio_path = DATA_DIR / "vm4_output.wav"

# stream audio and print chunk lengths
for chunk in stream_wav(str(audio_path)):
    print(len(chunk))
