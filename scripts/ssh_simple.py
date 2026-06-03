# SSH test using subprocess and echo password
import subprocess
import time

LUCKFOX_IP = "192.168.2.112"

try:
    print("=== Testing Luckfox via SSH ===")

    # Test 1: Check if we can connect
    print("\n1. Testing connection...")
    cmd = f'echo luckfox | ssh -o StrictHostKeyChecking=no root@{LUCKFOX_IP} "hostname"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Connection failed: {result.stderr}")
        print("\nTrying with explicit password input...")

    # Test 2: Try running existing program
    print("\n2. Checking for existing programs...")
    cmd = f'echo luckfox | ssh root@{LUCKFOX_IP} "ls -lh /oem/hello_* 2>/dev/null"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    print(result.stdout if result.stdout else "No programs found")

    # Test 3: Run hello_ultra if exists
    print("\n3. Testing hello_ultra (if exists)...")
    cmd = f'echo luckfox | ssh root@{LUCKFOX_IP} "/oem/hello_ultra 2>&1"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    print("="*60)
    print(result.stdout)
    print("="*60)

    if "hello, evfwt" in result.stdout:
        print("\n*** SUCCESS! ***")
    elif "Segmentation fault" in result.stdout:
        print("\nSegfault detected")
    elif "not found" in result.stdout or "No such file" in result.stdout:
        print("\nProgram not uploaded yet - need manual upload via SCP")
    else:
        print("\nUnknown result")

except Exception as e:
    print(f"ERROR: {e}")
