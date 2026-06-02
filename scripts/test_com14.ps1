# Test COM14 access
try {
    Write-Host "Testing COM14 access..."
    $port = New-Object System.IO.Ports.SerialPort COM14,115200,None,8,one
    $port.ReadTimeout = 1000
    $port.WriteTimeout = 1000
    $port.Open()
    Write-Host "SUCCESS: COM14 opened"

    $port.WriteLine("")
    Start-Sleep -Seconds 1
    $response = $port.ReadExisting()
    Write-Host "Response: $($response.Length) bytes"

    $port.Close()
    Write-Host "COM14 closed"
} catch {
    Write-Host "ERROR: $_"
    Write-Host "Exception Type: $($_.Exception.GetType().FullName)"
}
