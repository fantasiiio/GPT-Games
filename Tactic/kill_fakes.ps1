$processIDs = Get-Content -Path "processIDs.txt"

foreach ($processID in $processIDs) {
    Write-Host "Killing process with Process ID $processID"
    Stop-Process -Id $processID -Force
}

Remove-Item -Path "processIDs.txt"
