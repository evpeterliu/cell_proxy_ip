import serial
import time
import sys

def upload_file():
    base64_file = r"E:\claude\hello_evfwt.b64"
    remote_path = "/root/hello_evfwt"

    print("=== Luckfox File Upload via Serial ===")

    try:
        # Open serial port
        print("Opening COM14...")
        ser = serial.Serial('COM14', 115200, timeout=3)
        time.sleep(0.5)

        # Login
        print("Logging in...")
        ser.write(b"\n")
        time.sleep(1)
        ser.read_all()

        ser.write(b"root\n")
        time.sleep(2)
        ser.read_all()

        ser.write(b"luckfox\n")
        time.sleep(2)
        response = ser.read_all()
        print(f"Login response: {len(response)} bytes")

        # Clean old files
        print("Cleaning old files...")
        ser.write(f"rm -f {remote_path}.b64 {remote_path}\n".encode())
        time.sleep(1)
        ser.read_all()

        # Read base64 content
        print("Reading base64 file...")
        with open(base64_file, 'r') as f:
            content = f.read().strip()

        total_len = len(content)
        chunk_size = 500
        total_chunks = (total_len + chunk_size - 1) // chunk_size

        print(f"File size: {total_len} bytes")
        print(f"Chunks: {total_chunks}")
        print("Starting transfer...")

        # Transfer in chunks
        for i in range(total_chunks):
            start = i * chunk_size
            end = min(start + chunk_size, total_len)
            chunk = content[start:end]

            # Escape single quotes
            chunk = chunk.replace("'", "'\\''")

            cmd = f"echo -n '{chunk}' >> {remote_path}.b64\n"
            ser.write(cmd.encode())
            time.sleep(0.1)

            # Clear buffer
            if ser.in_waiting > 0:
                ser.read_all()

            # Progress
            if i % 100 == 0:
                percent = int(i * 100 / total_chunks)
                print(f"Progress: {percent}% ({i}/{total_chunks})")

        print("\nTransfer complete! Decoding...")

        # Decode base64
        ser.write(f"base64 -d {remote_path}.b64 > {remote_path}\n".encode())
        time.sleep(3)
        ser.read_all()

        # Set executable
        print("Setting executable permission...")
        ser.write(f"chmod +x {remote_path}\n".encode())
        time.sleep(1)
        ser.read_all()

        # Verify
        print("\nVerifying file...")
        ser.write(f"ls -lh {remote_path}\n".encode())
        time.sleep(1)
        response = ser.read_all().decode('utf-8', errors='ignore')
        print(response)

        # Test run
        print("=== Testing program ===")
        ser.write(f"{remote_path}\n".encode())
        time.sleep(2)
        response = ser.read_all().decode('utf-8', errors='ignore')
        print(response)

        # Cleanup
        ser.write(f"rm -f {remote_path}.b64\n".encode())
        time.sleep(1)

        ser.close()
        print("\n=== Upload successful! ===")

    except serial.SerialException as e:
        print(f"Serial port error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    upload_file()
