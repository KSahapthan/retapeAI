# test/streaming_test.py
from pathlib import Path
import sys
import time

# add project root to sys.path so we can import utils
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from utils.streaming import stream_wav

# path to the audio file
DATA_DIR = BASE_DIR / "data"
audio_path = DATA_DIR / "vm7_output.wav"

# constants for testing
CHUNK_MS = 20  
TARGET_SR = 8000 
# 16-bit PCM = 2 bytes per sample
EXPECTED_CHUNK_SIZE = int(TARGET_SR * CHUNK_MS / 1000) * 2  

start_time = time.time()

# test: Stream audio and assert chunk lengths
for chunk in stream_wav(str(audio_path)):
    assert len(chunk) == EXPECTED_CHUNK_SIZE, f"Chunk size mismatch: {len(chunk)} != {EXPECTED_CHUNK_SIZE}"

end_time = time.time()

# print execution time (on avg 1-2 sec delay)
print(f"Streaming completed in {end_time - start_time:.2f} seconds")