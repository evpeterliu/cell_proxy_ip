# Final verification - exit debug mode first
import serial
import time

try:
    print("=== Final Verification ===")
    ser = serial.Serial('COM14', 115200, timeout=5)
    time.sleep(0.5)

    # Clear buffers
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
    ser.read_all()

    # Try to exit debug mode
    print("\nStep 2: Attempting to exit debug mode...")
    ser.write(b"exit\r\n")
    time.sleep(1)
    ser.read_all()

    ser.write(b"quit\r\n")
    time.sleep(1)
    ser.read_all()

    # Try Ctrl+C
    ser.write(b"\x03")
    time.sleep(1)
    ser.read_all()

    # Check prompt
    ser.write(b"\r\n")
    time.sleep(1)
    prompt = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Current prompt: {repr(prompt)}")

    # Check file exists
    print("\nStep 3: Checking file...")
    ser.reset_input_buffer()
    ser.write(b"file /root/hello_evfwt\r\n")
    time.sleep(2)
    file_info = ser.read_all().decode('utf-8', errors='ignore')
    print(file_info)

    # Execute program
    print("\nStep 4: Executing program...")
    ser.reset_input_buffer()
    ser.write(b"/root/hello_evfwt\r\n")
    time.sleep(3)
    output = ser.read_all().decode('utf-8', errors='ignore')

    # Wait longer
    time.sleep(2)
    output += ser.read_all().decode('utf-8', errors='ignore')

    print("\n" + "="*50)
    print("OUTPUT:")
    print("="*50)
    print(output)
    print("="*50)

    # Check for expected output
    if "hello, evfwt" in output:
        print("\nSUCCESS: Program executed correctly!")
    else:
        print("\nWARNING: Expected output not found")

        # Try running with strace to see what happens
        print("\nStep 5: Running with strace...")
        ser.write(b"strace /root/hello_evfwt\r\n")
        time.sleep(3)
        strace_output = ser.read_all().decode('utf-8', errors='ignore')
        print(strace_output[:500])

    ser.close()
    print("\n=== Verification Complete ===")

except Exception as e:
    print(f"ERROR: {e}")
