# Check Luckfox network configuration
import serial
import time

def send_cmd(ser, cmd, wait=1.5):
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(wait)
    return ser.read_all().decode('utf-8', errors='ignore')

try:
    print("=== Checking Luckfox Network ===")
    ser = serial.Serial('COM14', 115200, timeout=5)
    time.sleep(0.5)

    # Login
    print("Logging in...")
    send_cmd(ser, "", 1)
    send_cmd(ser, "root", 2)
    send_cmd(ser, "luckfox", 2)

    # Check IP address
    print("\n1. IP Address:")
    output = send_cmd(ser, "ifconfig", 2)
    print(output)

    # Check if SSH is running
    print("\n2. SSH Service:")
    output = send_cmd(ser, "ps | grep ssh", 1)
    print(output)

    # Check SSH config
    print("\n3. Check sshd status:")
    output = send_cmd(ser, "netstat -tuln | grep 22", 1)
    print(output)

    # Get hostname
    print("\n4. Hostname:")
    output = send_cmd(ser, "hostname", 1)
    print(output)

    ser.close()

except Exception as e:
    print(f"ERROR: {e}")
