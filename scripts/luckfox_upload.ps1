# Luckfox File Upload via Serial Port
# Usage: .\luckfox_upload.ps1 -LocalFile "path\to\file" -RemotePath "/root/filename"

param(
    [Parameter(Mandatory=$true)]
    [string]$LocalFile,
    [Parameter(Mandatory=$true)]
    [string]$RemotePath
)

if (-not (Test-Path $LocalFile)) {
    Write-Error "File not found: $LocalFile"
    exit 1
}

$port = New-Object System.IO.Ports.SerialPort COM14,115200,None,8,one

try {
    # Read file and convert to base64
    $bytes = [System.IO.File]::ReadAllBytes($LocalFile)
    $base64 = [Convert]::ToBase64String($bytes)
    $fileSize = $bytes.Length

    Write-Host "File size: $fileSize bytes"
    Write-Host "Base64 size: $($base64.Length) chars"
    Write-Host "Uploading to: $RemotePath"

    $port.Open()
    Start-Sleep -Milliseconds 500

    # Login sequence
    Write-Host "Logging in..."
    $port.WriteLine("")
    Start-Sleep -Seconds 1
    $null = $port.ReadExisting()

    $port.WriteLine("root")
    Start-Sleep -Seconds 2
    $null = $port.ReadExisting()

    $port.WriteLine("luckfox")
    Start-Sleep -Seconds 2
    $null = $port.ReadExisting()

    # Remove old file if exists
    Write-Host "Preparing target file..."
    $port.WriteLine("rm -f $RemotePath.b64 $RemotePath")
    Start-Sleep -Seconds 1
    $null = $port.ReadExisting()

    # Split base64 into chunks (1000 chars per chunk to avoid buffer issues)
    $chunkSize = 1000
    $totalChunks = [Math]::Ceiling($base64.Length / $chunkSize)

    Write-Host "Transferring $totalChunks chunks..."

    for ($i = 0; $i -lt $totalChunks; $i++) {
        $start = $i * $chunkSize
        $length = [Math]::Min($chunkSize, $base64.Length - $start)
        $chunk = $base64.Substring($start, $length)

        # Append to file
        $port.WriteLine("echo -n '$chunk' >> $RemotePath.b64")
        Start-Sleep -Milliseconds 200
        $null = $port.ReadExisting()

        # Progress indicator
        $progress = [Math]::Floor(($i + 1) * 100 / $totalChunks)
        Write-Progress -Activity "Uploading" -Status "$progress% Complete" -PercentComplete $progress
    }

    Write-Progress -Activity "Uploading" -Completed
    Write-Host "Transfer complete, decoding..."

    # Decode base64
    $port.WriteLine("base64 -d $RemotePath.b64 > $RemotePath")
    Start-Sleep -Seconds 2
    $null = $port.ReadExisting()

    # Verify file size
    $port.WriteLine("ls -lh $RemotePath")
    Start-Sleep -Seconds 1
    $response = $port.ReadExisting()
    Write-Host "Verification:"
    Write-Host $response

    # Make executable if binary
    Write-Host "Setting executable permission..."
    $port.WriteLine("chmod +x $RemotePath")
    Start-Sleep -Seconds 1
    $null = $port.ReadExisting()

    # Clean up base64 file
    $port.WriteLine("rm -f $RemotePath.b64")
    Start-Sleep -Seconds 1

    Write-Host "`nUpload completed successfully!"
    Write-Host "File location: $RemotePath"

} catch {
    Write-Error "Upload error: $_"
} finally {
    if ($port.IsOpen) {
        $port.Close()
    }
}
