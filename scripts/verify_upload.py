# Test hello program with longer wait
import serial
import time

try:
    ser = serial.Serial('COM14', 115200, timeout=5)
    time.sleep(1)

    # Clear buffer
    ser.read_all()

    # Run program
    print("=== Executing /root/hello_evfwt ===")
    ser.write(b"/root/hello_evfwt\n")
    time.sleep(3)

    # Read all output
    output = ser.read_all().decode('utf-8', errors='ignore')
    print("Output:")
    print(output)
    print("="*40)

    # Also check file exists
    ser.write(b"ls -lh /root/hello_evfwt\n")
    time.sleep(1)
    file_info = ser.read_all().decode('utf-8', errors='ignore')
    print("File info:")
    print(file_info)

    ser.close()
except Exception as e:
    print(f"Error: {e}")
