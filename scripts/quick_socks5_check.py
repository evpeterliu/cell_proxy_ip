#!/usr/bin/env python3
# Quick SOCKS5 port checker
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

SERVER = "codex.adusun.com"
PORTS = range(21880, 21896)
USERNAME = "ppp"
PASSWORD = "ppp"

def test_port(port):
    """Test a single SOCKS5 port"""
    try:
        cmd = [
            "curl",
            "-x", f"socks5://{USERNAME}:{PASSWORD}@{SERVER}:{port}",
            "https://ip.sb",
            "--max-time", "5",
            "-s"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=6)

        if result.returncode == 0 and result.stdout.strip():
            ip = result.stdout.strip()
            return (port, True, ip)
        else:
            return (port, False, None)
    except Exception as e:
        return (port, False, None)

print("="*60)
print("SOCKS5 端口快速检测")
print(f"服务器: {SERVER}")
print(f"端口范围: 21880-21895")
print("="*60)

# Parallel testing
working = []
failed = []

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(test_port, port): port for port in PORTS}

    for future in as_completed(futures):
        port, status, ip = future.result()
        if status:
            working.append((port, ip))
            print(f"✅ {port} - {ip}")
        else:
            failed.append(port)
            print(f"❌ {port}")

print("\n" + "="*60)
print("汇总结果")
print("="*60)

print(f"\n✅ 可用端口 ({len(working)}个):")
for port, ip in sorted(working):
    print(f"  {port} -> {ip}")

print(f"\n❌ 不可用端口 ({len(failed)}个):")
print(f"  {', '.join(map(str, sorted(failed)))}")

print("\n" + "="*60)
