This project provides two Python scripts: **Record.py** and **Play.py**, designed for recording and playback of DMX data via Art-Net.

- **Record.py**: Captures incoming DMX data, saving it with timestamps into `.bin` files upon signal change.
- **Play.py**: Sends the recorded data back over Art-Net, allowing precise playback and optional synchronization with an accompanying MP3 audio file using `pygame.mixer`.

---

## 1. Using Record.py

The script passively listens for incoming Art-Net DMX packets and starts recording upon the first detection of data changes.

## Settings

The main parameters are located in the === SETTINGS === section within the file:

|Parameter|Default Value|Description|
|---|---|---|
|`UDP_IP`|`"127.0.0.1"`|IP address to listen on for Art-Net.|
|`UDP_PORT`|`6454`|Art-Net port (standard).|
|`TARGET_UNIVERSE`|`0`|The DMX Universe number to record.|
|`DURATION`|`225`|Recording duration in seconds.|
|`OUTPUT_DIR`|`"bins"`|Directory for saving `.bin` files.|

## Usage

```bash
python Record.py
```

---

## 2. Using Play.py

The script reads DMX data and timestamps from the `.bin` file and sends them to the network with precise timing intervals. Audio synchronization is also supported.

**Note on MP3 Files**

An **MP3 audio file is required** for synchronization. The script uses the `pygame.mixer` library to load and play audio simultaneously with the start of the DMX sequence. Audio files should be placed in the project's root folder. 

## Settings

The main parameters are located in the === SETTINGS === section within the file:

| Parameter              | Default Value            | Description                                                     |
| ---------------------- | ------------------------ | --------------------------------------------------------------- |
| `TARGET_IP`            | `"192.168.0.101"`        | The destination IP address for sending Art-Net packets.         |
| `UDP_PORT`             | `6454`                   | Art-Net port (standard).                                        |
| `UNIVERSE`             | `0`                      | The DMX Universe number to send data to.                        |
| `METRONOME_SOUND_FILE` | `"sounds/metronome.wav"` | Path to the countdown sound file.                               |
| `STOP_SOUND_FILE`      | `"sounds/stop.wav"`      | Path to the sound played when playback finishes or is stopped.  |

Usage

The script will launch an interactive menu to select the `.mp3` file (optional) and the `.bin` file: 


```bash
python Play.py
```

---
## 3. Requirements and Installation

Both scripts require **Python 3**.

The scripts utilize built-in libraries (`socket`, `time`, `struct`, `os`, `datetime`), but the audio functions of **Play.py** require the external `pygame` library.

Install `pygame` using pip:

```bash
pip install pygame
```
