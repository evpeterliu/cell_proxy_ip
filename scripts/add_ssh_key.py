import serial
import time

PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDAa69FXd7NdP2HXmgH37cK1f3pruBEqNRqzwlqPBh22UfhyrHMKsF3FoW58w6XgtPxwftKrwNtYBR4cXwYjDW0hdEJDVMn8sBDSzmPDplapPNEYUIGbuUvBFUxDoLKsmStq/ITEhRDFIB57WH/w0nAMi3PgawThiyYqauDYC8rx4+IbyRhWLGTo8qCbJ6wjI6YPuyLwaABHHDmmKxO2IL+xc72BhfJyOAu3bXpM4Vz/jgwIm5c9rboNKrFfBxPIFWKkRhjRf3kYmEoIbEU6Gm0GrzQoDj4o+axXkxSMr6qMnRuwUH3uMi1e0C1hOoKNCYHMcUwcPVBLa1E2mafJ51f claude@luckfox"

try:
    print("=== Adding SSH Key to Luckfox ===")

    ser = serial.Serial('COM14', 115200, timeout=3)
    time.sleep(0.5)

    # Login
    print("Logging in...")
    ser.write(b"\r\n"); time.sleep(1); ser.read_all()
    ser.write(b"root\r\n"); time.sleep(2); ser.read_all()
    ser.write(b"luckfox\r\n"); time.sleep(2); ser.read_all()

    # Create .ssh directory
    print("Creating .ssh directory...")
    ser.write(b"mkdir -p ~/.ssh\r\n")
    time.sleep(1)
    ser.read_all()

    # Add public key
    print("Adding public key...")
    cmd = f'echo "{PUBLIC_KEY}" >> ~/.ssh/authorized_keys\r\n'
    ser.write(cmd.encode())
    time.sleep(1)
    ser.read_all()

    # Set permissions
    print("Setting permissions...")
    ser.write(b"chmod 700 ~/.ssh\r\n")
    time.sleep(0.5)
    ser.read_all()

    ser.write(b"chmod 600 ~/.ssh/authorized_keys\r\n")
    time.sleep(0.5)
    ser.read_all()

    # Verify
    print("\nVerifying...")
    ser.write(b"ls -la ~/.ssh/\r\n")
    time.sleep(1)
    output = ser.read_all().decode('utf-8', errors='ignore')
    print(output)

    ser.write(b"tail -1 ~/.ssh/authorized_keys\r\n")
    time.sleep(1)
    output = ser.read_all().decode('utf-8', errors='ignore')
    print(output)

    ser.close()

    print("\n=== SSH Key Added Successfully! ===")
    print("\nYou can now SSH without password:")
    print("ssh -i /tmp/luckfox_key root@192.168.2.112")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
