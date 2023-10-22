param (
    [int]$endValue
)

# Check if $N is provided
if (-not $endValue) {
    Write-Host "Please provide a value for N."
    exit
}

if ($endValue -lt 1) {
    Write-Host "Please provide a value greater than 0 for N."
    exit
}

# Generate a shuffled list of numbers from 0 to $endValue
$randomNumbers = 0..($endValue-1) | Get-Random -Count ($endValue)

$processIDs = @()

foreach ($num in $randomNumbers) {
    Write-Host "Starting process with parameter $num"
    $process = Start-Process -FilePath "python" -ArgumentList "MainFrame.py", "-ai", "$num" -NoNewWindow -PassThru
    $processIDs += $process.Id
}

$processIDs | Out-File -FilePath "processIDs.txt"