# Upload and test GOARM=5 version
import serial
import time

def send_cmd(ser, cmd, wait=1.5):
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(wait)
    return ser.read_all().decode('utf-8', errors='ignore')

try:
    print("=== Upload and Test GOARM=5 Version ===")

    base64_file = r"E:\claude\hello_arm5.b64"
    remote_path = "/oem/hello_arm5"

    ser = serial.Serial('COM14', 115200, timeout=5)
    time.sleep(0.5)

    # Login
    print("1. Logging in...")
    send_cmd(ser, "", 1)
    send_cmd(ser, "root", 2)
    send_cmd(ser, "luckfox", 2)

    # Read base64 content
    print("\n2. Reading base64 file...")
    with open(base64_file, 'r') as f:
        content = f.read().strip()

    total_len = len(content)
    chunk_size = 500
    total_chunks = (total_len + chunk_size - 1) // chunk_size

    print(f"   File size: {total_len} bytes")
    print(f"   Chunks: {total_chunks}")

    # Clean old file
    send_cmd(ser, f"rm -f {remote_path}.b64 {remote_path}", 1)

    # Transfer in chunks
    print("\n3. Transferring...")
    for i in range(total_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, total_len)
        chunk = content[start:end]

        chunk = chunk.replace("'", "'\\''")
        cmd = f"echo -n '{chunk}' >> {remote_path}.b64\r\n"
        ser.write(cmd.encode())
        time.sleep(0.1)

        if ser.in_waiting > 0:
            ser.read_all()

        if i % 500 == 0:
            percent = int(i * 100 / total_chunks)
            print(f"   Progress: {percent}% ({i}/{total_chunks})")

    print("   Transfer complete!")

    # Decode
    print("\n4. Decoding base64...")
    send_cmd(ser, f"base64 -d {remote_path}.b64 > {remote_path}", 3)

    # Set executable
    send_cmd(ser, f"chmod +x {remote_path}", 1)

    # Check file
    print("\n5. Verifying file...")
    output = send_cmd(ser, f"ls -lh {remote_path}", 1)
    print(output)

    # RUN THE PROGRAM
    print("\n6. RUNNING PROGRAM (GOARM=5)...")
    print("="*60)
    ser.reset_input_buffer()
    output = send_cmd(ser, f"{remote_path}", 3)
    print(output)
    print("="*60)

    # Check result
    if "hello, evfwt" in output:
        print("\nSUCCESS WITH GOARM=5!")
    elif "Segmentation fault" in output:
        print("\nStill segfault with GOARM=5")
    elif "Illegal instruction" in output:
        print("\nIllegal instruction with GOARM=5")
    else:
        print(f"\nUnexpected output: {repr(output)}")

    # Clean up base64
    send_cmd(ser, f"rm -f {remote_path}.b64", 1)

    ser.close()
    print("\n=== Test Complete ===")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
