# Luckfox Simple Program Upload Script
# This uploads hello_evfwt program to Luckfox via COM14

Write-Host "=== Luckfox Program Upload via Serial ==="

# Base64 encoded program (hello_evfwt)
$base64Program = @"
f0VMRgEBAQAAAAAAAAAAAAIAKAABAAAAEN0HADQAAAD0AAAAAgAABTQAIAAGACgADgANAAYAAAA0
AAAANAABADQAAQDAAAAAwAAAAAQAAAAAAAEABAAAAJwPAACcDwEAnA8BAGQAAABkAAAABAAAAAQA
AAABAAAAAAAAAAAAAQAAAAEAvOcIALznCAAFAAAAAAABAA
"@

# Note: The above is truncated. Full base64 is 1.7MB
# To use this script:
# 1. Get the full base64 content from hello_evfwt.b64
# 2. Replace the truncated content above
# 3. Or use the file-based version below

$useFileMode = $true
$base64File = "E:\claude\hello_evfwt.b64"
$remotePath = "/root/hello_evfwt"

$port = New-Object System.IO.Ports.SerialPort COM14,115200,None,8,one

try {
    Write-Host "Opening COM14..."
    $port.Open()
    Start-Sleep -Milliseconds 500

    # Login
    Write-Host "Logging in to Luckfox..."
    $port.WriteLine("")
    Start-Sleep -Seconds 1
    $null = $port.ReadExisting()

    $port.WriteLine("root")
    Start-Sleep -Seconds 2
    $null = $port.ReadExisting()

    $port.WriteLine("luckfox")
    Start-Sleep -Seconds 2
    $response = $port.ReadExisting()
    Write-Host "Login response: $($response.Length) bytes"

    # Clean old files
    Write-Host "Cleaning old files..."
    $port.WriteLine("rm -f $remotePath.b64 $remotePath")
    Start-Sleep -Seconds 1
    $null = $port.ReadExisting()

    if ($useFileMode -and (Test-Path $base64File)) {
        Write-Host "Reading base64 from file: $base64File"
        $base64Content = Get-Content $base64File -Raw
    } else {
        Write-Host "Using embedded base64 content"
        $base64Content = $base64Program
    }

    # Remove whitespace
    $base64Content = $base64Content -replace '\s+',''
    $totalLength = $base64Content.Length
    Write-Host "Base64 length: $totalLength bytes"

    # Transfer in chunks
    $chunkSize = 400
    $totalChunks = [Math]::Ceiling($totalLength / $chunkSize)
    Write-Host "Transferring $totalChunks chunks..."

    for ($i = 0; $i -lt $totalChunks; $i++) {
        $start = $i * $chunkSize
        $length = [Math]::Min($chunkSize, $totalLength - $start)
        $chunk = $base64Content.Substring($start, $length)

        # Append to remote file
        $port.WriteLine("echo -n '$chunk' >> $remotePath.b64")
        Start-Sleep -Milliseconds 100

        # Clear buffer
        if ($port.BytesToRead -gt 0) {
            $null = $port.ReadExisting()
        }

        # Progress every 100 chunks
        if ($i % 100 -eq 0) {
            $percent = [Math]::Floor($i * 100 / $totalChunks)
            Write-Host "Progress: $percent% ($i/$totalChunks)"
        }
    }

    Write-Host "`nTransfer complete! Decoding..."

    # Decode base64 to binary
    $port.WriteLine("base64 -d $remotePath.b64 > $remotePath")
    Start-Sleep -Seconds 5
    if ($port.BytesToRead -gt 0) {
        $response = $port.ReadExisting()
        Write-Host "Decode response: $response"
    }

    # Set executable permission
    Write-Host "Setting executable permission..."
    $port.WriteLine("chmod +x $remotePath")
    Start-Sleep -Seconds 1
    $null = $port.ReadExisting()

    # Verify file
    Write-Host "`nVerifying uploaded file..."
    $port.WriteLine("ls -lh $remotePath")
    Start-Sleep -Seconds 1
    $response = $port.ReadExisting()
    Write-Host $response

    # Test run
    Write-Host "`n=== Testing program ==="
    $port.WriteLine("$remotePath")
    Start-Sleep -Seconds 2
    $response = $port.ReadExisting()
    Write-Host $response

    # Clean up base64 file
    $port.WriteLine("rm -f $remotePath.b64")
    Start-Sleep -Seconds 1

    Write-Host "`n=== Upload and test complete! ==="

} catch {
    Write-Error "Error: $_"
} finally {
    if ($port.IsOpen) {
        $port.Close()
        Write-Host "Serial port closed"
    }
}
