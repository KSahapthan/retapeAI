# retape.ai Assignment

Voicemail drop systems must determine the **correct moment to send the message** — after a greeting has ended or a beep has occurred — without relying on speech understanding or manual intervention

This assignment focuses on the **timing problem** in compliant voicemail drops:  
accurately detecting when a call recipient has finished speaking or when a beep signals readiness, under strict latency and reliability constraints

The solution operates purely at the **audio signal level**, making deterministic decisions based on speech activity, silence, and tone detection

## Features

- **Voice Activity Detection (VAD)**  
  Detects the end of a greeting by analyzing speech-to-silence transitions and, in some cases, implicitly captures the end of a beep

- **Beep Detection**  
  Uses a normalized Goertzel-based approach to detect the start and end of beep tones across a predefined frequency range

- **Parallel Processing**  
  Runs VAD and beep detection simultaneously using threading to minimize detection latency and improve robustness

- **Timeout Handling**  
  Triggers voicemail playback if neither a greeting end nor a beep is detected within a configurable time window

- **Lightweight & Deterministic Design**  
  Avoids STT and LLMs to ensure predictable behavior, low compute overhead, and language-agnostic operation


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

| Audio Sample # | Approx Manual Timestamp (ms) |   Type   | Predicted Timestamp (ms) | Predicted Via | Accuracy |
|:--------------:|:----------------------------:|:--------:|:------------------------:|:-------------:|:--------:|
| 1              | 10000                         | Beep     | 11940                   | VAD           | ✅       |
| 2              | 9000                          | Beep     | 10300                   | VAD           | ✅       |
| 3              | 15000                         | Beep     | 10940                   | VAD           | ❌       |
| 4              | 5000                          | No Beep  | 6140                    | VAD           | ✅       |
| 5              | 15000                         | No Beep  | 15680                   | VAD           | ✅       |
| 6              | 5000                          | No Beep  | 5160                    | VAD           | ✅       |
| 7              | 12000                         | Beep     | 12780                   | Beep          | ✅       |



## Observations & Limitations

- **No-Beep Scenarios (Audio Samples 4, 5, 6)**  
  VAD correctly detected silence in the absence of a beep, enabling accurate voicemail triggering

- **Audio Samples 1 & 2**  
  VAD successfully detected the **end of the beep** even without explicit beep-detection logic

- **Beep Detection Logic**  
  The dedicated beep-detection logic correctly identified the beep **only in Audio Sample 7**

- **Audio Sample 3 (Failure Case)**  
  A **long silence gap between the greeting end and the beep** makes beep detection **infeasible** under the current architecture/workflow

## Reasoning for Choice of Method (No STT / No LLM)

- **Task Scope is Temporal, Not Semantic**  
  The problem is centered around detecting **audio events and silence boundaries**, not understanding spoken content. Speech-to-Text and LLMs operate at a semantic level, which is unnecessary for this use case

- **Latency and Cost Constraints**  
  STT and LLM-based pipelines introduce additional latency and operational cost, while VAD-based approaches operate in near-real-time with minimal compute overhead

- **Deterministic and Predictable Behavior**  
  Signal-processing methods (VAD + beep heuristics) provide deterministic outcomes, making system behavior easier to reason about, debug, and tune compared to probabilistic LLM outputs

- **Robustness to Language and Accent Variations**  
  The approach is language-agnostic and unaffected by accents, pronunciation, or transcription errors, which are common failure modes for STT systems

- **Architectural Simplicity**  
  Avoiding STT and LLMs keeps the pipeline simple, lightweight, and easier to maintain, while still achieving acceptable accuracy for the defined problem constraints