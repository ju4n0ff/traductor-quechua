$url = "https://github.com/ju4n0ff/traductor-quechua/releases/download/v1.0.0/Traductor.Quechua.exe"
$outDir = Join-Path $PSScriptRoot "dist"
$outFile = Join-Path $outDir "Traductor Quechua.exe"

if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

if (-not (Test-Path $outFile)) {
    Write-Output "Descargando Traductor Quechua.exe..."
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $url -OutFile $outFile
    Write-Output "Descargado en: $outFile"
} else {
    Write-Output "El archivo ya existe: $outFile"
}
