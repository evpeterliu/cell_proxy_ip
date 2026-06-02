# Final verification - must see "hello, evfwt" output
import serial
import time

try:
    print("=== Final Verification ===")
    ser = serial.Serial('COM14', 115200, timeout=5)
    time.sleep(0.5)

    # Clear any existing data
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # Login sequence
    print("Step 1: Logging in...")
    ser.write(b"\r\n")
    time.sleep(1)
    ser.read_all()

    ser.write(b"root\r\n")
    time.sleep(2)
    ser.read_all()

    ser.write(b"luckfox\r\n")
    time.sleep(2)
    login_resp = ser.read_all()
    print(f"Login complete: {len(login_resp)} bytes received")

    # Check if file exists
    print("\nStep 2: Checking file existence...")
    ser.write(b"ls -lh /root/hello_evfwt\r\n")
    time.sleep(1)
    file_check = ser.read_all().decode('utf-8', errors='ignore')
    print(file_check)

    if 'No such file' in file_check or 'cannot access' in file_check:
        print("ERROR: File does not exist!")
        ser.close()
        exit(1)

    # Execute the program
    print("\nStep 3: Executing program...")
    ser.reset_input_buffer()
    ser.write(b"/root/hello_evfwt\r\n")

    # Wait and collect output
    time.sleep(2)
    output = ser.read_all().decode('utf-8', errors='ignore')

    # Try again with longer wait
    time.sleep(2)
    output += ser.read_all().decode('utf-8', errors='ignore')

    print("\n" + "="*50)
    print("PROGRAM OUTPUT:")
    print("="*50)
    print(output)
    print("="*50)

    # Verify expected output
    if "hello, evfwt" in output:
        print("\n✅ SUCCESS: Program executed and produced expected output!")
    elif "hello" in output.lower():
        print("\n⚠️ PARTIAL: Found 'hello' but not complete expected output")
    else:
        print("\n❌ FAILED: Expected output 'hello, evfwt' not found")
        print("Attempting alternative execution method...")

        # Try with explicit shell
        ser.write(b"sh -c '/root/hello_evfwt'\r\n")
        time.sleep(3)
        alt_output = ser.read_all().decode('utf-8', errors='ignore')
        print("\nAlternative output:")
        print(alt_output)

    ser.close()
    print("\n=== Verification Complete ===")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
