# Try to reboot or reset the device
import serial
import time

try:
    print("=== Device Reset Attempt ===")
    ser = serial.Serial('COM14', 115200, timeout=5)
    time.sleep(0.5)

    # Try reboot command
    print("\n1. Attempting reboot...")
    ser.write(b"reboot\r\n")
    time.sleep(2)
    resp = ser.read_all()
    print(f"Response: {resp.decode('utf-8', errors='ignore')}")

    # Send DTR/RTS signals to reset device
    print("\n2. Toggling DTR/RTS...")
    ser.setDTR(False)
    ser.setRTS(False)
    time.sleep(0.5)
    ser.setDTR(True)
    ser.setRTS(True)
    time.sleep(1)

    # Wait for boot
    print("\n3. Waiting for boot sequence...")
    time.sleep(10)

    # Collect boot messages
    boot_msg = ser.read_all().decode('utf-8', errors='ignore')
    print("Boot messages:")
    print(boot_msg[:500] if len(boot_msg) > 500 else boot_msg)

    # Try to login again
    print("\n4. Attempting fresh login...")
    time.sleep(2)
    ser.write(b"\r\n")
    time.sleep(1)

    prompt = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Prompt: {repr(prompt)}")

    if "login:" in prompt.lower():
        print("Login prompt detected!")
        ser.write(b"root\r\n")
        time.sleep(2)
        resp = ser.read_all().decode('utf-8', errors='ignore')
        print(f"After root: {resp}")

        if "Password" in resp or "password" in resp:
            ser.write(b"luckfox\r\n")
            time.sleep(2)
            resp = ser.read_all().decode('utf-8', errors='ignore')
            print(f"After password: {resp}")
    elif "debug>" in prompt:
        print("Still in debug mode - reboot did not work")
    else:
        print(f"Unknown prompt: {prompt}")

    # Try running program
    print("\n5. Running program...")
    ser.write(b"/root/hello_evfwt\r\n")
    time.sleep(3)
    output = ser.read_all().decode('utf-8', errors='ignore')

    print("="*60)
    print(output)
    print("="*60)

    if "hello, evfwt" in output:
        print("\nSUCCESS!")
    elif "debug>" in output and output.count("debug>") > 1:
        print("\nSTILL IN DEBUG MODE - Device may need physical reset")
        print("Recommendation: Power cycle the Luckfox device")
    else:
        print("\nUnclear result")

    ser.close()

except Exception as e:
    print(f"ERROR: {e}")
