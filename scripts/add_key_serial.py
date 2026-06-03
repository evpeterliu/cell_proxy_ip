import serial
import time

PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDAa69FXd7NdP2HXmgH37cK1f3pruBEqNRqzwlqPBh22UfhyrHMKsF3FoW58w6XgtPxwftKrwNtYBR4cXwYjDW0hdEJDVMn8sBDSzmPDplapPNEYUIGbuUvBFUxDoLKsmStq/ITEhRDFIB57WH/w0nAMi3PgawThiyYqauDYC8rx4+IbyRhWLGTo8qCbJ6wjI6YPuyLwaABHHDmmKxO2IL+xc72BhfJyOAu3bXpM4Vz/jgwIm5c9rboNKrFfBxPIFWKkRhjRf3kYmEoIbEU6Gm0GrzQoDj4o+axXkxSMr6qMnRuwUH3uMi1e0C1hOoKNCYHMcUwcPVBLa1E2mafJ51f claude@luckfox"

def send_cmd(ser, cmd, wait=1):
    """Send command and read response"""
    ser.reset_input_buffer()
    ser.write(f"{cmd}\n".encode())
    time.sleep(wait)
    return ser.read_all().decode('utf-8', errors='ignore')

try:
    print("=== Adding SSH Key via Serial ===")

    ser = serial.Serial('COM14', 115200, timeout=3)
    time.sleep(1)

    # Clear buffer and send enters to wake up
    print("Waking up serial...")
    ser.write(b"\n\n\n")
    time.sleep(2)
    ser.read_all()

    # Login
    print("Logging in as root...")
    send_cmd(ser, "root", 2)
    send_cmd(ser, "luckfox", 2)

    # Test if we're logged in
    print("Testing login...")
    output = send_cmd(ser, "whoami", 1)
    if "root" not in output:
        print("Login may have failed, but continuing...")

    # Create .ssh directory
    print("\n1. Creating .ssh directory...")
    output = send_cmd(ser, "mkdir -p ~/.ssh", 1)
    print(f"   Output: {output[:100] if output else 'OK'}")

    # Add the key (split into smaller chunks to avoid buffer issues)
    print("\n2. Adding SSH public key...")
    # Clear the file first
    send_cmd(ser, "rm -f ~/.ssh/authorized_keys", 1)

    # Add key
    cmd = f"echo '{PUBLIC_KEY}' > ~/.ssh/authorized_keys"
    output = send_cmd(ser, cmd, 1)
    print(f"   Output: {output[:100] if output else 'OK'}")

    # Set permissions
    print("\n3. Setting permissions...")
    send_cmd(ser, "chmod 700 ~/.ssh", 0.5)
    send_cmd(ser, "chmod 600 ~/.ssh/authorized_keys", 0.5)

    # Verify
    print("\n4. Verifying...")
    output = send_cmd(ser, "ls -la ~/.ssh/", 2)
    print(output)

    print("\n5. Checking key content...")
    output = send_cmd(ser, "wc -c ~/.ssh/authorized_keys", 1)
    print(f"   File size: {output}")

    output = send_cmd(ser, "head -c 50 ~/.ssh/authorized_keys", 1)
    print(f"   First 50 chars: {output}")

    ser.close()

    print("\n" + "="*60)
    print("SSH KEY SETUP COMPLETE!")
    print("="*60)
    print("\nNow testing SSH connection from cloud...")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
