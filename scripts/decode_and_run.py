# Decode and run the program NOW
import serial
import time

def send_cmd(ser, cmd, wait=1.5):
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(wait)
    return ser.read_all().decode('utf-8', errors='ignore')

try:
    print("=== Decode and Execute ===")
    ser = serial.Serial('COM14', 115200, timeout=5)
    time.sleep(0.5)

    # Login
    print("Logging in...")
    send_cmd(ser, "", 1)
    send_cmd(ser, "root", 2)
    send_cmd(ser, "luckfox", 2)

    # Decode base64 file
    print("\n1. Decoding base64 to binary...")
    output = send_cmd(ser, "base64 -d /root/hello_evfwt.b64 > /root/hello_evfwt", 3)
    print(output)

    # Check file size
    print("\n2. Checking decoded file...")
    output = send_cmd(ser, "ls -lh /root/hello_evfwt", 1)
    print(output)

    # Make executable
    print("\n3. Setting executable permission...")
    output = send_cmd(ser, "chmod +x /root/hello_evfwt", 1)
    print(output)

    # Verify it's an ELF binary
    print("\n4. Checking file type...")
    output = send_cmd(ser, "file /root/hello_evfwt", 1)
    print(output)

    # Run the program!
    print("\n5. RUNNING THE PROGRAM...")
    print("="*60)
    ser.reset_input_buffer()
    output = send_cmd(ser, "/root/hello_evfwt", 3)
    print(output)
    print("="*60)

    # Check result
    if "hello, evfwt" in output:
        print("\n" + "🎉"*20)
        print("SUCCESS! Program executed correctly!")
        print("Output: 'hello, evfwt' detected!")
        print("🎉"*20)
    else:
        print("\nProgram executed but output unclear.")
        print("Let me try running again...")
        output = send_cmd(ser, "/root/hello_evfwt", 3)
        print(output)
        if "hello, evfwt" in output:
            print("\nSUCCESS on second try!")

    # Also copy to persistent storage
    print("\n6. Copying to persistent storage (/oem/)...")
    output = send_cmd(ser, "cp /root/hello_evfwt /oem/hello_evfwt && ls -lh /oem/hello_evfwt", 2)
    print(output)

    ser.close()
    print("\n=== Complete ===")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
