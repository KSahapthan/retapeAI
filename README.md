# RetapeAI

RetapeAI is a simple yet effective audio processing tool designed to detect voicemail triggers using two primary methods:

1. **Beep Detection**: Identifies the start and end of a beep sound.
2. **VAD (Voice Activity Detection)**: Detects the end of a greeting based on speech and silence patterns.

The system runs both detection methods in parallel, ensuring accurate and timely voicemail triggering.

---

## Features
- **Beep Detection**: Uses Goertzel's algorithm to detect a 1000 Hz beep.
- **VAD Detection**: Analyzes audio energy levels to identify speech and silence.
- **Parallel Processing**: Runs both detection methods simultaneously for efficiency.
- **Timeout Handling**: Triggers voicemail if no event is detected within a specified time.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/retapeAI.git
   cd retapeAI
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Command-Line

1. Place your audio file in the `data/` directory.
2. Run the `when_to_start.py` script:
   ```bash
   python src/when_to_start.py
   ```
3. The script will process the audio and print the detected events:
   - Beep detected
   - Greeting end detected
   - Timeout

### Example Output
```json
{
    "timestamp_ms": 1200,
    "mode": "beep",
    "status": "sent"
}
```

---

## Project Structure

```
retapeAI/
├── data/                  # Audio files for processing
├── src/                   # Source code
│   ├── beep.py            # Beep detection logic
│   ├── vad.py             # VAD detection logic
│   ├── when_to_start.py   # Main script
│   └── ...
├── utils/                 # Utility functions
│   ├── calculate_goertzel.py # Goertzel algorithm implementation
│   ├── streaming.py       # Audio streaming utilities
│   └── ...
└── README.md              # Project documentation
```

---

## How It Works

1. **Beep Detection**:
   - Uses Goertzel's algorithm to detect a 1000 Hz tone.
   - Confirms beep start and end based on consecutive audio chunks.

2. **VAD Detection**:
   - Monitors RMS energy levels to detect speech and silence.
   - Confirms greeting end after a period of silence following speech.

3. **Parallel Execution**:
   - Both detection methods run in separate threads.
   - The first detected event triggers the voicemail.

---

## Configuration

- **Beep Detection**:
  - `TARGET_FREQ`: Frequency of the beep (default: 1000 Hz).
  - `THRESHOLD`: Power threshold for beep detection.

- **VAD Detection**:
  - `ENERGY_THRESHOLD`: RMS energy threshold for speech detection.
  - `MIN_SPEECH_MS`: Minimum speech duration to confirm greeting start.
  - `MIN_SILENCE_MS`: Minimum silence duration to confirm greeting end.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.

---

## Contact

For questions or feedback, please contact [your-email@example.com].

---

## Results

| Audio Sample Number | Approx Manual Timestamp (ms) | Type      | Predicted Timestamp (ms) | Predicted via the Type |
|---------------------|-----------------------------|-----------|--------------------------|------------------------|
| 1                   | 1000                        | Beep      | --                       | VAD                    |
| 2                   | 9000                        | Beep      | --                       | VAD                    |
| 3                   | 15000                       | Beep      | --                       | VAD+beep               |
| 4                   | 5000                        | No Beep   | --                       | VAD                    |
| 5                   | 15000                       | No Beep   | --                       | VAD                    |
| 6                   | 5000                        | No Beep   | --                       | VAD                    |
| 7                   | 12000                       | Beep      | --                       | beep                   |