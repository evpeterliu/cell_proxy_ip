# Quick get IP address and test connection
import serial
import time

try:
    print("=== Quick Network Check ===")
    ser = serial.Serial('COM14', 115200, timeout=3)
    time.sleep(0.5)

    # Login
    ser.write(b"\r\n")
    time.sleep(1)
    ser.read_all()

    ser.write(b"root\r\n")
    time.sleep(2)
    ser.read_all()

    ser.write(b"luckfox\r\n")
    time.sleep(2)
    ser.read_all()

    # Get IP quickly
    print("\nGetting IP address...")
    ser.reset_input_buffer()
    ser.write(b"ip addr show\r\n")
    time.sleep(2)
    output = ser.read_all().decode('utf-8', errors='ignore')
    print(output)

    # Extract IP
    import re
    ips = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', output)
    if ips:
        print(f"\nFound IPs: {ips}")
        for ip in ips:
            if not ip.startswith('127.'):
                print(f"\n*** Luckfox IP: {ip} ***")

    # Check SSH
    print("\nChecking SSH service...")
    ser.write(b"ps | grep sshd\r\n")
    time.sleep(1)
    output = ser.read_all().decode('utf-8', errors='ignore')
    print(output)

    ser.close()

except Exception as e:
    print(f"ERROR: {e}")
