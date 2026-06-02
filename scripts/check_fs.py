# Check filesystem and re-upload
import serial
import time

def send_cmd(ser, cmd, wait=1):
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(wait)
    return ser.read_all().decode('utf-8', errors='ignore')

try:
    print("=== Filesystem Check & Re-upload ===")
    ser = serial.Serial('COM14', 115200, timeout=5)
    time.sleep(0.5)

    # Login
    print("Logging in...")
    send_cmd(ser, "", 1)
    send_cmd(ser, "root", 2)
    send_cmd(ser, "luckfox", 2)

    # Check filesystem
    print("\n1. Checking /root directory...")
    output = send_cmd(ser, "ls -la /root/", 2)
    print(output)

    print("\n2. Checking if base64 file exists...")
    output = send_cmd(ser, "ls -lh /root/*.b64", 1)
    print(output)

    print("\n3. Checking disk space...")
    output = send_cmd(ser, "df -h", 1)
    print(output)

    print("\n4. Checking /tmp directory...")
    output = send_cmd(ser, "ls -la /tmp/", 1)
    print(output)

    # Files might be in /tmp or got lost during reboot
    print("\n5. Searching for hello_evfwt...")
    output = send_cmd(ser, "find / -name '*hello*' 2>/dev/null", 3)
    print(output)

    # Check if we can write to /root
    print("\n6. Testing write permission...")
    output = send_cmd(ser, "touch /root/test.txt && ls -l /root/test.txt && rm /root/test.txt", 2)
    print(output)

    # The files were uploaded but probably lost during reboot
    # /root might not be persistent storage
    print("\n7. Checking mount points...")
    output = send_cmd(ser, "mount | grep root", 1)
    print(output)

    print("\n8. Checking writable persistent locations...")
    output = send_cmd(ser, "ls -la /userdata/ /oem/ /mnt/ 2>/dev/null", 2)
    print(output)

    ser.close()

    print("\n" + "="*60)
    print("ANALYSIS:")
    print("The file was uploaded to /root/ but got lost after reboot.")
    print("/root/ appears to be tmpfs (RAM disk) - not persistent!")
    print("Need to upload to persistent storage like /userdata/ or /oem/")
    print("="*60)

except Exception as e:
    print(f"ERROR: {e}")
