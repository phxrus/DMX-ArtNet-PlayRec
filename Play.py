import socket
import time
import struct
import os
import pygame.mixer

# === SETTINGS ===
TARGET_IP = "192.168.0.101"
UDP_PORT = 6454
UNIVERSE = 0
FRAME_SIZE = 4 + 512
METRONOME_SOUND_FILE = "sounds/metronome.wav" # Path updated
STOP_SOUND_FILE = "sounds/stop.wav" # Path updated
# =================

def clear_console():
    """Clears the console depending on the OS."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_file_selection(file_extension="", directory="."):
    """
    Displays a file selection menu for the specified extension in the given directory.
    If one file is found, it is selected automatically.
    """
    files = [f for f in os.listdir(directory) if f.endswith(file_extension.strip('*'))]

    # Adding directory prefix to filenames for correct operation
    files = [os.path.join(directory, f) for f in files]

    if not files:
        print(f"\n[!] Files {file_extension} not found in directory {directory}.")
        return None

    files.sort()

    # Logic for automatic selection of an mp3 file if it's the only one (extension not empty)
    if len(files) == 1 and file_extension == "*.mp3":
        print(f"\n[PREPARING] Found single audio file: {files[0]}. Selecting automatically.")
        return files[0] # Returning the full path to the file

    print(f"\n" + "="*40)
    print(f" LIST OF {file_extension} FILES FOR SELECTION (Folder: {directory})")
    print("="*40)
    for i, filename in enumerate([os.path.basename(f) for f in files], 1): # Showing only the filename in the menu
        print(f"{i}. {filename}")
    print("="*40)

    while True:
        choice = input("Enter the file number to start (or 'q' to exit): ")
        if choice.lower() == 'q': return "exit"
        try:
            index = int(choice) - 1
            if 0 <= index < len(files): return files[index] # Returning the full path to the selected file
            else: print(f"Error: enter a number from 1 to {len(files)}")
        except ValueError: print("Error: enter a correct number or 'q'.")

def play_selected_file(filename, audio_file=None):

    metronome_sound = None
    stop_sound = None

    try:
        pygame.mixer.init()
        if audio_file and os.path.exists(audio_file):
            pygame.mixer.music.load(audio_file)
            print(f"Audio file loaded: {audio_file}")

        if os.path.exists(METRONOME_SOUND_FILE):
            metronome_sound = pygame.mixer.Sound(METRONOME_SOUND_FILE)
            print(f"Metronome sound loaded: {METRONOME_SOUND_FILE}")

        if os.path.exists(STOP_SOUND_FILE):
            stop_sound = pygame.mixer.Sound(STOP_SOUND_FILE)
            print(f"Stop sound loaded: {STOP_SOUND_FILE}")

    except pygame.error as e:
        print(f"Error loading audio/metronome: {e}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    artnet_header = bytearray(b'Art-Net\x00\x00\x50\x00\x0e\x00\x00')
    artnet_header.append(UNIVERSE & 0xFF)
    artnet_header.append((UNIVERSE >> 8) & 0xFF)
    artnet_header.extend([0x02, 0x00])

    try:
        with open(filename, "rb") as f:
            first_frame = f.read(FRAME_SIZE)
            if not first_frame: return
            sock.sendto(artnet_header + first_frame[4:], (TARGET_IP, UDP_PORT))

            print(f"\n[PREPARING] DMX File: {filename}")
            input("Fixtures in position. Press ENTER to START...")

            print("STARTING PLAYBACK IN:")
            for i in range(3, 0, -1):
                if metronome_sound:
                    metronome_sound.play()
                print(f"{i} sec.", end='\r')
                time.sleep(1)
                print(" " * 10, end='\r')

            print(">>> PLAYING... (Ctrl+C for interruption)")
            start_play = time.time()

            if audio_file:
                pygame.mixer.music.play()

            while True:
                chunk = f.read(FRAME_SIZE)
                if not chunk: break

                target_time = struct.unpack('f', chunk[:4])[0] # Extracting the value from the tuple
                dmx_data = chunk[4:]

                current_elapsed = time.time() - start_play
                wait = target_time - current_elapsed
                if wait > 0: time.sleep(wait)

                sock.sendto(artnet_header + dmx_data, (TARGET_IP, UDP_PORT))
                print(f"Progress: {round(target_time, 1)} sec. ", end='\r') # Extracting the value from the tuple

    except KeyboardInterrupt:
        print("\n[!] Playback interrupted by user.")
    except Exception as e:
        print(f"\n[!] Error: {e}")
    finally:
        sock.close()
        if audio_file:
            pygame.mixer.music.stop()

        if stop_sound:
            stop_sound.play()
        time.sleep(1)

    print("\n--- Finished ---")

def main():
    while True:
        clear_console()

        # Selecting an MP3 file in the current directory (.)
        selected_audio = get_file_selection(file_extension="*.mp3", directory=".")
        if selected_audio == "exit":
            print("Program terminated.")
            break

        if not selected_audio:
            selected_audio = None

        # Selecting a BIN file in the subdirectory (bins)
        selected_file = get_file_selection(file_extension="*.bin", directory="bins")

        if selected_file == "exit":
            print("Program terminated.")
            break

        if selected_file:
            play_selected_file(selected_file, audio_file=selected_audio)
            input("\nPress ENTER to return to the file selection menu...")
        else:
            input("\nPress ENTER to refresh the list...")

if __name__ == "__main__":
    clear_console()
    main()
