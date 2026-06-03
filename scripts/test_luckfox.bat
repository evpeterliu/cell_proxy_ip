@echo off
REM Manual test script for Luckfox via SSH
echo ============================================
echo Luckfox Go Program Test Script
echo ============================================
echo.

echo Step 1: Testing SSH connection...
ssh -o ConnectTimeout=5 root@192.168.2.112 "hostname && uname -a"
echo.

echo Step 2: Checking existing programs...
ssh root@192.168.2.112 "ls -lh /oem/hello_* /root/hello_* 2>/dev/null"
echo.

echo Step 3: Running hello_ultra (GOARM=5)...
echo ============================================
ssh root@192.168.2.112 "/oem/hello_ultra"
echo ============================================
echo.

echo Step 4: If segfault, try hello_arm5...
ssh root@192.168.2.112 "/oem/hello_arm5"
echo.

echo Step 5: If segfault, try hello_arm6...
ssh root@192.168.2.112 "/oem/hello_arm6"
echo.

echo Test complete!
pause
