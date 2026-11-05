$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeRoot = Join-Path (Split-Path -Parent $projectRoot) 'portfolio-build-tools'
$pgCtl = Join-Path $runtimeRoot 'pgsql\bin\pg_ctl.exe'
$pgData = Join-Path $runtimeRoot 'pgdata'
if (!(Test-Path -LiteralPath $pgCtl) -or !(Test-Path -LiteralPath $pgData)) {
    throw 'Local bundled runtime is unavailable. Use the Docker Compose setup in README.md.'
}
& $pgCtl -D $pgData status
if ($LASTEXITCODE -eq 0) { return }
$pgLog = Join-Path $runtimeRoot 'postgres.log'
$arguments = @('-D',('"'+$pgData+'"'),'-l',('"'+$pgLog+'"'),'-o','"-p 55432 -h 127.0.0.1"','-w','start')
$process = Start-Process -FilePath $pgCtl -ArgumentList $arguments -WindowStyle Hidden -PassThru
if (!$process.WaitForExit(30000)) { throw 'PostgreSQL startup timed out. Inspect the local postgres.log.' }
if ($process.ExitCode -ne 0) { throw 'PostgreSQL startup failed. Inspect the local postgres.log.' }
Write-Output 'Local PostgreSQL is ready on 127.0.0.1:55432.'
