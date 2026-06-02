# Try different line endings and control sequences
import serial
import time

try:
    print("=== Debug Mode Analysis ===")
    ser = serial.Serial('COM14', 115200, timeout=5)
    time.sleep(0.5)

    # Clear everything
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # Send just Enter with different line endings
    print("\n1. Testing line endings...")

    ser.write(b"\n")
    time.sleep(1)
    resp1 = ser.read_all()
    print(f"\\n response: {repr(resp1)}")

    ser.write(b"\r")
    time.sleep(1)
    resp2 = ser.read_all()
    print(f"\\r response: {repr(resp2)}")

    ser.write(b"\r\n")
    time.sleep(1)
    resp3 = ser.read_all()
    print(f"\\r\\n response: {repr(resp3)}")

    # Try sending without line ending
    print("\n2. Testing raw command...")
    ser.write(b"ls")
    time.sleep(0.5)
    resp = ser.read_all()
    print(f"Raw 'ls': {repr(resp)}")

    ser.write(b"\r\n")
    time.sleep(1)
    resp = ser.read_all()
    print(f"After \\r\\n: {repr(resp)}")

    # Check if we're actually logged in
    print("\n3. Checking login state...")
    ser.write(b"root\r\n")
    time.sleep(2)
    resp = ser.read_all()
    print(f"After 'root': {repr(resp)}")

    if b"Password" in resp or b"password" in resp:
        print("Password prompt detected!")
        ser.write(b"luckfox\r\n")
        time.sleep(2)
        resp = ser.read_all()
        print(f"After password: {repr(resp)}")

    # Try to get a real prompt
    print("\n4. Trying to get shell prompt...")
    ser.write(b"whoami\r\n")
    time.sleep(1)
    resp = ser.read_all()
    print(f"whoami: {resp.decode('utf-8', errors='ignore')}")

    # Actually run the program
    print("\n5. Attempting program execution...")
    ser.reset_input_buffer()
    ser.write(b"/root/hello_evfwt\r\n")
    time.sleep(3)

    output = ser.read_all().decode('utf-8', errors='ignore')
    print("="*60)
    print("RAW OUTPUT:")
    print(repr(output))
    print("="*60)
    print("DECODED OUTPUT:")
    print(output)
    print("="*60)

    # Check for success
    if "hello" in output.lower() or "evfwt" in output:
        print("\nSUCCESS: Program output detected!")
    else:
        print("\nFAILURE: No program output detected")
        print("\nThis appears to be a non-functional shell or boot mode")

    ser.close()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
