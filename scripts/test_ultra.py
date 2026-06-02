# Quick upload and test ultra simple version
import serial
import time

def send_cmd(ser, cmd, wait=1.5):
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(wait)
    return ser.read_all().decode('utf-8', errors='ignore')

try:
    print("=== Quick Test: Ultra Simple Version ===")

    base64_file = r"E:\claude\hello_ultra.b64"
    remote_path = "/oem/hello_ultra"

    ser = serial.Serial('COM14', 115200, timeout=5)
    time.sleep(0.5)

    # Login
    print("Logging in...")
    send_cmd(ser, "", 1)
    send_cmd(ser, "root", 2)
    send_cmd(ser, "luckfox", 2)

    # Read and transfer
    print("Reading and transferring...")
    with open(base64_file, 'r') as f:
        content = f.read().strip()

    chunk_size = 500
    total_chunks = (len(content) + chunk_size - 1) // chunk_size
    print(f"Total chunks: {total_chunks}")

    send_cmd(ser, f"rm -f {remote_path}.b64 {remote_path}", 1)

    for i in range(total_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, len(content))
        chunk = content[start:end].replace("'", "'\\''")
        ser.write(f"echo -n '{chunk}' >> {remote_path}.b64\r\n".encode())
        time.sleep(0.08)
        if ser.in_waiting > 0:
            ser.read_all()
        if i % 1000 == 0:
            print(f"  {int(i*100/total_chunks)}%")

    print("Transfer done. Decoding...")
    send_cmd(ser, f"base64 -d {remote_path}.b64 > {remote_path}", 3)
    send_cmd(ser, f"chmod +x {remote_path}", 1)

    # Run immediately
    print("\n" + "="*60)
    print("RUNNING ULTRA SIMPLE VERSION:")
    print("="*60)
    ser.reset_input_buffer()
    output = send_cmd(ser, f"{remote_path}", 3)
    print(output)
    print("="*60)

    if "hello, evfwt" in output:
        print("\n*** SUCCESS! Ultra simple version works! ***")
        result = "SUCCESS"
    elif "Segmentation fault" in output:
        print("\nStill segfault")
        result = "SEGFAULT"
    elif "Illegal instruction" in output:
        print("\nIllegal instruction")
        result = "ILLEGAL"
    else:
        print(f"\nUnknown: {repr(output[:200])}")
        result = "UNKNOWN"

    # Cleanup
    send_cmd(ser, f"rm -f {remote_path}.b64", 1)
    ser.close()

    print(f"\n=== Result: {result} ===")

except Exception as e:
    print(f"ERROR: {e}")
