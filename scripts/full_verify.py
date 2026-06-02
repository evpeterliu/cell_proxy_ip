# Complete verification with login
import serial
import time

def send_and_wait(ser, command, wait_time=1):
    ser.write(f"{command}\n".encode())
    time.sleep(wait_time)
    return ser.read_all().decode('utf-8', errors='ignore')

try:
    print("=== Luckfox Program Verification ===")
    ser = serial.Serial('COM14', 115200, timeout=3)
    time.sleep(0.5)

    # Login sequence
    print("Logging in...")
    ser.write(b"\n")
    time.sleep(1)
    ser.read_all()

    ser.write(b"root\n")
    time.sleep(2)
    ser.read_all()

    ser.write(b"luckfox\n")
    time.sleep(2)
    ser.read_all()

    print("Logged in successfully!\n")

    # Check file exists
    print("1. Checking file...")
    output = send_and_wait(ser, "ls -lh /root/hello_evfwt", 1)
    print(output)

    # Check file type
    print("2. Checking file type...")
    output = send_and_wait(ser, "file /root/hello_evfwt", 1)
    print(output)

    # Run program
    print("3. Running program...")
    output = send_and_wait(ser, "/root/hello_evfwt", 3)
    print(output)

    # Also try with explicit path
    print("4. Running with explicit path...")
    output = send_and_wait(ser, "cd /root && ./hello_evfwt", 3)
    print(output)

    ser.close()
    print("\n=== Verification complete ===")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
