import serial
import time

def cmd(ser, c, wait=1.5):
    ser.reset_input_buffer()
    ser.write(f"{c}\r\n".encode())
    time.sleep(wait)
    return ser.read_all().decode('utf-8', errors='ignore')

try:
    ser = serial.Serial('COM14', 115200, timeout=3)
    time.sleep(0.5)
    # login
    ser.write(b"\r\n"); time.sleep(1); ser.read_all()
    ser.write(b"root\r\n"); time.sleep(2); ser.read_all()
    ser.write(b"luckfox\r\n"); time.sleep(2); ser.read_all()

    print("===== CPU INFO =====")
    print(cmd(ser, "cat /proc/cpuinfo", 2))

    print("===== ELF HEADER (hello_evfwt) =====")
    print(cmd(ser, "od -An -tx1 -N 52 /root/hello_evfwt", 2))

    print("===== LDD / libc =====")
    print(cmd(ser, "ls -la /lib/ld-* /lib/libc* 2>&1", 2))

    print("===== uname =====")
    print(cmd(ser, "uname -a", 1))

    print("===== dmesg segfault =====")
    print(cmd(ser, "dmesg | tail -15", 2))

    ser.close()
except Exception as e:
    print(f"ERROR: {e}")
