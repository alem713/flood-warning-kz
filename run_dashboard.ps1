$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonCandidates = @(
    "C:\Users\Serik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    "python"
)

$python = $null
foreach ($candidate in $pythonCandidates) {
    try {
        if ($candidate -eq "python") {
            $resolved = Get-Command python -ErrorAction Stop
            $python = $resolved.Source
        } elseif (Test-Path $candidate) {
            $python = $candidate
        }
        if ($python) { break }
    } catch { }
}

if (-not $python) {
    throw "Python was not found. Install Python or update run_dashboard.ps1 with a valid interpreter path."
}

$stdoutLog = Join-Path $projectRoot "streamlit.out.log"
$stderrLog = Join-Path $projectRoot "streamlit.err.log"

while ($true) {
    Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') Starting Streamlit..."
    $process = Start-Process `
        -FilePath $python `
        -ArgumentList @(
            "-m", "streamlit", "run", "dashboard/app.py",
            "--server.port", "8501",
            "--server.headless", "true",
            "--server.fileWatcherType", "none"
        ) `
        -WorkingDirectory $projectRoot `
        -RedirectStandardOutput $stdoutLog `
        -RedirectStandardError $stderrLog `
        -PassThru

    Wait-Process -Id $process.Id
    Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') Streamlit stopped. Restarting in 3 seconds..."
    Start-Sleep -Seconds 3
}
