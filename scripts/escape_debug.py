# Try to escape debug mode and get to real shell
import serial
import time

def send_command(ser, cmd, wait=1.5):
    """Send command and return output"""
    ser.reset_input_buffer()
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(wait)
    return ser.read_all().decode('utf-8', errors='ignore')

try:
    print("=== Escape Debug Mode ===")
    ser = serial.Serial('COM14', 115200, timeout=5)
    time.sleep(0.5)

    # Login
    print("Logging in...")
    send_command(ser, "", 1)
    send_command(ser, "root", 2)
    send_command(ser, "luckfox", 2)

    # Try various escape methods
    print("\n1. Trying 'sh'...")
    output = send_command(ser, "sh", 2)
    print(output)

    print("\n2. Trying '/bin/sh'...")
    output = send_command(ser, "/bin/sh", 2)
    print(output)

    print("\n3. Trying 'bash'...")
    output = send_command(ser, "bash", 2)
    print(output)

    print("\n4. Trying '/bin/bash'...")
    output = send_command(ser, "/bin/bash", 2)
    print(output)

    # Check what shell we're in
    print("\n5. Checking current shell...")
    output = send_command(ser, "echo $SHELL", 2)
    print(f"Shell: {output}")

    # Check prompt variable
    print("\n6. Checking PS1...")
    output = send_command(ser, "echo $PS1", 2)
    print(f"PS1: {output}")

    # Try to run program directly
    print("\n7. Running program with absolute path...")
    output = send_command(ser, "/root/hello_evfwt", 3)
    print("="*50)
    print(output)
    print("="*50)

    if "hello, evfwt" in output:
        print("\nSUCCESS!")
    else:
        # Try with exec
        print("\n8. Trying exec...")
        output = send_command(ser, "exec /root/hello_evfwt", 3)
        print(output)

        if "hello, evfwt" in output:
            print("\nSUCCESS with exec!")
        else:
            # Check if file is actually executable
            print("\n9. Checking file permissions and type...")
            output = send_command(ser, "ls -la /root/hello_evfwt", 1)
            print(output)

            output = send_command(ser, "file /root/hello_evfwt", 1)
            print(output)

            # Try running with explicit interpreter
            print("\n10. Checking if it's ELF...")
            output = send_command(ser, "hexdump -C /root/hello_evfwt | head -1", 2)
            print(output)

    ser.close()

except Exception as e:
    print(f"ERROR: {e}")
