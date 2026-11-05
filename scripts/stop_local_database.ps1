$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeRoot = Join-Path (Split-Path -Parent $projectRoot) 'portfolio-build-tools'
$pgCtl = Join-Path $runtimeRoot 'pgsql\bin\pg_ctl.exe'
$pgData = Join-Path $runtimeRoot 'pgdata'
if (!(Test-Path -LiteralPath $pgCtl) -or !(Test-Path -LiteralPath $pgData)) { throw 'Local runtime is unavailable.' }
& $pgCtl -D $pgData -m fast -w stop
if ($LASTEXITCODE -ne 0) { throw 'Unable to stop the local portfolio database.' }
