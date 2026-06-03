import serial
import time

print("=== Upload hello_arm5_soft (GOARM=5) ===")

try:
    # Read base64 file
    with open(r'E:\claude\hello_arm5_soft.b64', 'r') as f:
        b64_content = f.read().strip()

    print(f"File size: {len(b64_content)} bytes, {len(b64_content.splitlines())} lines")

    ser = serial.Serial('COM14', 115200, timeout=3)
    time.sleep(0.5)

    # Login
    ser.write(b"\r\n"); time.sleep(1); ser.read_all()
    ser.write(b"root\r\n"); time.sleep(2); ser.read_all()
    ser.write(b"luckfox\r\n"); time.sleep(2); ser.read_all()

    # Prepare target file
    print("\nPreparing target file...")
    ser.write(b"rm -f /root/hello_arm5_soft.b64 /root/hello_arm5_soft\r\n")
    time.sleep(1)
    ser.read_all()

    # Upload in chunks
    print("Uploading base64 (this takes ~3 minutes)...")
    lines = b64_content.splitlines()
    total = len(lines)

    for i, line in enumerate(lines):
        cmd = f'echo "{line}" >> /root/hello_arm5_soft.b64\r\n'
        ser.write(cmd.encode())
        time.sleep(0.02)

        if i % 500 == 0:
            ser.read_all()
            print(f"  {int(i*100/total)}% ({i}/{total})", flush=True)

    print("  100% - Upload complete!")
    time.sleep(1)
    ser.read_all()

    # Decode
    print("\nDecoding...")
    ser.write(b"base64 -d /root/hello_arm5_soft.b64 > /root/hello_arm5_soft\r\n")
    time.sleep(3)
    ser.read_all()

    # Set permissions
    print("Setting permissions...")
    ser.write(b"chmod +x /root/hello_arm5_soft\r\n")
    time.sleep(1)
    ser.read_all()

    # Verify
    print("\nVerifying...")
    ser.write(b"ls -lh /root/hello_arm5_soft\r\n")
    time.sleep(1)
    output = ser.read_all().decode('utf-8', errors='ignore')
    print(output)

    # TEST RUN!
    print("\n" + "="*60)
    print("TESTING PROGRAM:")
    print("="*60)
    ser.reset_input_buffer()
    ser.write(b"/root/hello_arm5_soft\r\n")
    time.sleep(2)
    output = ser.read_all().decode('utf-8', errors='ignore')
    print(output)
    print("="*60)

    if "hello, evfwt" in output:
        print("\n*** SUCCESS! GOARM=5 WORKS! ***")
    elif "Segmentation fault" in output:
        print("\nStill segfault with GOARM=5")
    else:
        print("\nUnexpected output")

    # Cleanup b64
    ser.write(b"rm -f /root/hello_arm5_soft.b64\r\n")
    time.sleep(0.5)

    ser.close()
    print("\nDone!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
