# SSH to Luckfox and test Go program
import paramiko
import time

LUCKFOX_IP = "192.168.2.112"
USERNAME = "root"
PASSWORD = "luckfox"

try:
    print("=== SSH Connection to Luckfox ===")

    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"Connecting to {LUCKFOX_IP}...")
    ssh.connect(LUCKFOX_IP, username=USERNAME, password=PASSWORD, timeout=10)
    print("Connected!")

    # Check system info
    print("\n1. System Info:")
    stdin, stdout, stderr = ssh.exec_command("hostname && uname -a")
    print(stdout.read().decode())

    # Check if program exists
    print("\n2. Checking existing programs:")
    stdin, stdout, stderr = ssh.exec_command("ls -lh /oem/hello_* /root/hello_* 2>/dev/null")
    output = stdout.read().decode()
    print(output if output else "No programs found")

    # Upload hello_ultra using SFTP
    print("\n3. Uploading hello_ultra...")
    sftp = ssh.open_sftp()
    local_file = r"E:\claude\hello_ultra.b64"
    remote_file = "/oem/hello_ultra.b64"

    try:
        sftp.put(local_file, remote_file)
        print(f"Uploaded {local_file} -> {remote_file}")
    except Exception as e:
        print(f"Upload failed: {e}")
        print("Trying alternative upload method...")

        # Alternative: read and write in chunks
        with open(local_file, 'r') as f:
            content = f.read()

        # Write via SSH commands
        ssh.exec_command(f"rm -f {remote_file}")
        time.sleep(0.5)

        chunk_size = 50000
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size].replace("'", "'\\''")
            cmd = f"echo -n '{chunk}' >> {remote_file}"
            ssh.exec_command(cmd)
            time.sleep(0.1)
            print(f"  {int(i*100/len(content))}%", end='\r')
        print("  100% - Upload complete")

    # Decode and run
    print("\n4. Decoding base64...")
    stdin, stdout, stderr = ssh.exec_command(
        "base64 -d /oem/hello_ultra.b64 > /oem/hello_ultra && "
        "chmod +x /oem/hello_ultra && "
        "ls -lh /oem/hello_ultra"
    )
    time.sleep(2)
    print(stdout.read().decode())

    # RUN THE PROGRAM!
    print("\n5. RUNNING PROGRAM:")
    print("="*60)
    stdin, stdout, stderr = ssh.exec_command("/oem/hello_ultra")
    time.sleep(2)

    output = stdout.read().decode()
    error = stderr.read().decode()

    print(output)
    if error:
        print(f"STDERR: {error}")
    print("="*60)

    # Check result
    if "hello, evfwt" in output:
        print("\n*** SUCCESS! Program works! ***")
    elif "Segmentation fault" in error or "Segmentation fault" in output:
        print("\nStill segfault with ultra version")
    else:
        print(f"\nUnexpected result")

    # Cleanup
    ssh.exec_command("rm -f /oem/hello_ultra.b64")

    sftp.close()
    ssh.close()
    print("\n=== Done ===")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
