# retape.ai assignment

The retape.ai assignment is a simple yet effective audio processing tool designed to detect voicemail triggers using two primary methods:

1. **VAD (Voice Activity Detection)**: Detects the end of a greeting based on speech and silence patterns, also identifies end of a beep
2. **Beep Detection**: Identifies the start and end of a beep sound

The system runs both detection methods in parallel, ensuring accurate and timely voicemail triggering.

## Features
- **Beep Detection**: Uses Goertzel's algorithm (normalized version) to detect a range of beep frequencies
- **VAD Detection**: Analyzes audio energy levels via ratios to identify speech and silence
- **Parallel Processing**: Runs both detection methods simultaneously for efficiency using Threading
- **Timeout Handling**: Triggers voicemail if no event is detected within a specified time 

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/KSahapthan/retapeAI.git
   cd retapeAI
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command-Line

1. Place your audio files in the `data/` directory.
2. Run the `main.py` script to process all `.wav` files:
   ```bash
   python src/main.py
   ```
3. To process a specific file, uncomment the relevant section in `main.py` and specify the file name.

### Example Output
```json
{
    "timestamp_ms": 1200,
    "mode": "beep",
    "status": "sent"
}
```

## Project Structure

```
retapeAI/
├── data/                  # Audio files for processing
├── src/                   # Source code
│   ├── beep.py            # Beep detection logic
│   ├── vad.py             # VAD detection logic
│   ├── main.py            # Main script for batch processing
│   └── ...
├── utils/                 # Utility functions
│   ├── calculate_goertzel.py # Goertzel algorithm implementation
│   ├── streaming.py       # Audio streaming utilities
│   └── ...
├── test/                  # Test scripts
│   ├── streaming_test.py  # Test for streaming functionality
│   └── ...
└── README.md              # Project documentation
```
 
## Configuration

- **Beep Detection**:
  - `BEEP_FREQS`: List of frequencies to monitor for a beep.
  - `RATIO_THRESHOLD`: Minimum ratio of beep energy to total energy to confirm a beep.
  - `CONSECUTIVE_REQD`: Number of consecutive chunks required to confirm a beep start.

- **VAD Detection**:
  - `ENERGY_THRESHOLD`: RMS energy threshold for speech detection.
  - `MIN_SPEECH_MS`: Minimum speech duration to confirm greeting start.
  - `MIN_SILENCE_MS`: Minimum silence duration to confirm greeting end.

## Results

| Audio Sample # | Approx Manual Timestamp (ms) | Type    | Predicted Timestamp (ms) | Predicted Via | Accuracy |
|---------------:|------------------------------:|---------|--------------------------:|---------------|:--------:|
| 1              | 10000                         | Beep    | 11940                     | VAD           | ✅ |
| 2              | 9000                          | Beep    | 10300                     | VAD           | ✅ |
| 3              | 15000                         | Beep    | 10940                     | VAD           | ❌ |
| 4              | 5000                          | No Beep | 6140                      | VAD           | ✅ |
| 5              | 15000                         | No Beep | 15680                     | VAD           | ✅ |
| 6              | 5000                          | No Beep | 5160                      | VAD           | ✅ |
| 7              | 12000                         | Beep    | 12780                     | Beep          | ✅ |



## Observations & Limitations

- **Audio Samples 1 & 2**  
  VAD successfully detected the **end of the beep**, even without explicit beep detection

- **Beep Detection Logic**  
  The dedicated beep logic correctly detected the beep **only in Audio Sample 7**

- **Audio Sample 3 (Failure Case)**  
  There is a **long silence gap between the greeting end and the beep**, which makes beep detection **not feasible** under the current architecture/workflow
