# Quick test via serial
import serial
import time

try:
    ser = serial.Serial('COM14', 115200, timeout=2)
    time.sleep(0.5)

    # Send command to run program
    ser.write(b"\n")
    time.sleep(0.5)
    ser.read_all()

    print("Running /root/hello_evfwt...")
    ser.write(b"/root/hello_evfwt\n")
    time.sleep(2)

    output = ser.read_all().decode('utf-8', errors='ignore')
    print(output)

    ser.close()
except Exception as e:
    print(f"Error: {e}")
