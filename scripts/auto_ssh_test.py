# Auto SSH test - comprehensive check
import subprocess
import time

LUCKFOX_IP = "192.168.2.112"

def run_ssh_cmd(cmd, timeout=10):
    """Run SSH command with password"""
    full_cmd = f'ssh -o ConnectTimeout={timeout} -o StrictHostKeyChecking=no root@{LUCKFOX_IP} "{cmd}"'

    print(f"\n> {cmd}")
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=timeout)

    output = result.stdout.strip()
    error = result.stderr.strip()

    if output:
        print(output)
    if error and "password" not in error.lower():
        print(f"[ERROR] {error}")

    return result.returncode, output, error

try:
    print("="*70)
    print("LUCKFOX AUTO TEST - Comprehensive Program Verification")
    print("="*70)

    # Step 1: Connection test
    print("\n[1/7] Testing SSH connection...")
    ret, out, err = run_ssh_cmd("hostname && uname -m")
    if ret != 0:
        print("SSH connection failed!")
        print("Please manually run: ssh root@192.168.2.112")
        print("Password: luckfox")
        exit(1)
    print("Connected to Luckfox")

    # Step 2: Check filesystem
    print("\n[2/7] Checking filesystem...")
    run_ssh_cmd("df -h | grep -E 'oem|userdata|root'")

    # Step 3: List uploaded files
    print("\n[3/7] Checking uploaded files...")
    ret, out, err = run_ssh_cmd("ls -lh /oem/hello_* /root/hello_* 2>&1")

    has_files = False
    if "hello_" in out:
        has_files = True
        print("Found uploaded programs")
    else:
        print("No programs found - need to upload")

    # Step 4: Check if decoded
    print("\n[4/7] Checking if programs are decoded...")
    ret, out, err = run_ssh_cmd("file /oem/hello_ultra /oem/hello_arm5 2>&1 | head -5")

    # Step 5: Try running hello_ultra (GOARM=5 ultra simple)
    print("\n[5/7] Testing hello_ultra (GOARM=5 ultra simple)...")
    print("="*70)
    ret, out, err = run_ssh_cmd("/oem/hello_ultra 2>&1", timeout=5)
    print("="*70)

    success_program = None

    if "hello, evfwt" in out:
        print("\nSUCCESS! hello_ultra works!")
        success_program = "hello_ultra"
    elif "Segmentation fault" in out or "Segmentation fault" in err:
        print("Segfault with hello_ultra")

        # Try hello_arm5
        print("\n[6/7] Testing hello_arm5 (GOARM=5 standard)...")
        print("="*70)
        ret, out, err = run_ssh_cmd("/oem/hello_arm5 2>&1", timeout=5)
        print("="*70)

        if "hello, evfwt" in out:
            print("\nSUCCESS! hello_arm5 works!")
            success_program = "hello_arm5"
        elif "Segmentation fault" in out or "Segmentation fault" in err:
            print("Segfault with hello_arm5")

            # Try hello_arm6
            print("\n[7/7] Testing hello_arm6 (GOARM=6)...")
            print("="*70)
            ret, out, err = run_ssh_cmd("/oem/hello_arm6 2>&1", timeout=5)
            print("="*70)

            if "hello, evfwt" in out:
                print("\nSUCCESS! hello_arm6 works!")
                success_program = "hello_arm6"
            else:
                print("All versions failed")

    # Final report
    print("\n" + "="*70)
    print("FINAL REPORT")
    print("="*70)

    if success_program:
        print(f"\nSUCCESS! Working program: {success_program}")
        print("\nCommands for manual verification:")
        print("-" * 70)
        print(f"ssh root@192.168.2.112")
        print(f"# Password: luckfox")
        print(f"")
        print(f"# Then run:")
        print(f"/oem/{success_program}")
        print(f"")
        print(f"# Expected output:")
        print(f"hello, evfwt")
        print("-" * 70)
    else:
        print("\nNo working version found")
        print("\nPossible issues:")
        print("1. Files not uploaded correctly")
        print("2. Need different compilation flags")
        print("3. Architecture incompatibility")

    print("\n" + "="*70)

except subprocess.TimeoutExpired:
    print("\nSSH command timeout")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
