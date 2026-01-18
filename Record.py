import socket
import time
import struct
import os # Import the os module
from datetime import datetime

# === SETTINGS ===
UDP_IP = "127.0.0.1"
UDP_PORT = 6454
TARGET_UNIVERSE = 0
DURATION = 225 # Recording duration in seconds
OUTPUT_DIR = "bins" # New directory for files

def record_binary_autoname():
    # Create the directory if it does not exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Directory '{OUTPUT_DIR}' created.")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((UDP_IP, UDP_PORT))
    except Exception as e:
        print(f"Error: {e}")
        return

    is_recording = False
    start_time = 0
    last_dmx = None
    frames_count = 0
    file_handle = None
    
    print(f"--- Waiting changes DMX signal (Universe: {TARGET_UNIVERSE}) ---")
    
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            
            if len(data) < 18: continue
            if data[0:8] == b'Art-Net\x00':
                opcode = data[8] | (data[9] << 8)
                universe = data[14] | (data[15] << 8)
                
                if opcode == 0x5000 and universe == TARGET_UNIVERSE:
                    current_dmx = data[18:530]
                    
                    # TRIGGER LOGIC
                    if not is_recording:
                        if last_dmx is None:
                            last_dmx = current_dmx
                            continue
                        
                        if current_dmx != last_dmx:
                            is_recording = True
                            start_time = time.time()
                            
                            # Generate file name by current date
                            now = datetime.now()
                            filename = now.strftime("DMX-%Y-%m-%d-%H-%M-%S.bin")
                            
                            # Combine directory and file name
                            filepath = os.path.join(OUTPUT_DIR, filename)
                            
                            # Open the file only after the trigger
                            file_handle = open(filepath, "wb")
                            print(f"\n>>> СТАРТ ЗАПИСИ: {filename} в {OUTPUT_DIR}")
                        else:
                            continue
                    
                    # RECORDING PROCESS
                    elapsed = time.time() - start_time
                    
                    # Write timestamp (4 bytes) and 512 bytes DMX
                    timestamp_bin = struct.pack('f', elapsed)
                    file_handle.write(timestamp_bin + current_dmx)
                    
                    frames_count += 1
                    print(f"Frames: {frames_count} | Time: {round(elapsed, 1)}s", end='\r')
                    
                    if elapsed >= DURATION:
                        break
                        
    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
    finally:
        sock.close()
        if file_handle:
            file_handle.close()
        if is_recording:
            print(f"\nDone. File saved in {OUTPUT_DIR}.")
        else:
            print("\nRecording was not started.")
    
if __name__ == "__main__":
    record_binary_autoname()
