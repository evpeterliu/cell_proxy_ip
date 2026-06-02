# Luckfox Pico Serial Communication Script
# Usage: .\luckfox_serial.ps1 "command"
# Example: .\luckfox_serial.ps1 "uname -a"

param(
    [Parameter(Mandatory=$true)]
    [string]$Command,
    [int]$ReadDelay = 2
)

$port = New-Object System.IO.Ports.SerialPort COM14,115200,None,8,one

try {
    $port.Open()
    Start-Sleep -Milliseconds 500

    # Login sequence
    $port.WriteLine("")
    Start-Sleep -Seconds 1
    $null = $port.ReadExisting()

    $port.WriteLine("root")
    Start-Sleep -Seconds 2
    $null = $port.ReadExisting()

    $port.WriteLine("luckfox")
    Start-Sleep -Seconds 2
    $null = $port.ReadExisting()

    # Execute command
    $port.WriteLine($Command)
    Start-Sleep -Seconds $ReadDelay

    # Read response
    if ($port.BytesToRead -gt 0) {
        $response = $port.ReadExisting()
        Write-Output $response
    }

} catch {
    Write-Error "Serial communication error: $_"
} finally {
    if ($port.IsOpen) {
        $port.Close()
    }
}
