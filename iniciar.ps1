# =============================================================================
#  Librería Salesiana Don Bosco - arranque en modo LOCAL (sin Docker para las apps)
#
#    Comercial  -> http://localhost:5001
#    Inventario -> http://localhost:5000
#    phpMyAdmin -> http://localhost:8080
#
#  Docker solo se usa para las bases de datos MySQL.
# =============================================================================

param(
    [switch]$SoloBases,
    [switch]$ConDatos
)

$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $MyCommandPath
Set-Location $raiz

function Titulo($t) {
    Write-Host ""
    Write-Host "=== $t ===" -ForegroundColor Cyan
}

# ---------------------------------------------------------------------------
Titulo "1/4  Levantando las bases de datos (Docker)"
docker compose up -d db_comercial db_inventario phpmyadmin
if ($LASTEXITCODE -ne 0) { Write-Host "No se pudieron levantar las bases." -ForegroundColor Red; exit 1 }

Write-Host "Esperando a que MySQL quede listo..." -ForegroundColor DarkGray
$listo = $false
for ($i = 0; $i -lt 40; $i++) {
    $salida = docker exec db_comercial mysqladmin ping -h localhost -uroot -prootpass 2>&1
    if ($LASTEXITCODE -eq 0) { $listo = $true; break }
    Start-Sleep -Seconds 3
}
if (-not $listo) { Write-Host "MySQL no respondió a tiempo." -ForegroundColor Red; exit 1 }
Write-Host "MySQL listo." -ForegroundColor Green

if ($ConDatos) {
    Titulo "1b  Cargando datos de demostración"
    docker run --rm --network microservicios-libreria_microservicios_net `
        -v "${raiz}\bd:/bd" `
        -e COM_HOST=db_comercial -e INV_HOST=db_inventario `
        -e COM_USER=root -e COM_PASS=rootpass `
        -e INV_USER=root -e INV_PASS=rootpass `
        python:3.11-slim sh -c "pip install --quiet pymysql && python /bd/seed.py"
}

if ($SoloBases) {
    Titulo "Listo. Solo bases de datos activas."
    Write-Host "  phpMyAdmin : http://localhost:8080  (root / rootpass)" -ForegroundColor Green
    Write-Host "  Comercial  : http://localhost:5001  (admin@admin.com / admin123)" -ForegroundColor Green
    Write-Host "  Inventario : http://localhost:5000  (admin@admin.com / admin123)" -ForegroundColor Green
    exit 0
}

# ---------------------------------------------------------------------------
Titulo "2/4  Preparando los entornos de Python"

$py = $null
foreach ($c in @("python", "py -3.11", "python3")) {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if ($cmd) { $py = $c; break }
}
if (-not $py) {
    Write-Host "No se encontro Python. Instalalo con:" -ForegroundColor Red
    Write-Host "  winget install Python.Python.3.11" -ForegroundColor Yellow
    exit 1
}
Write-Host "Python: $py" -ForegroundColor DarkGray

$servicios = @(
    @{ Nombre = "comercial";  Carpeta = "Comercial" },
    @{ Nombre = "inventario"; Carpeta = "Inventario y gestión interna" }
)

foreach ($s in $servicios) {
    $dir = Join-Path $raiz $s.Carpeta
    $venv = Join-Path $dir ".venv"

    if (-not (Test-Path $venv)) {
        Write-Host "Creando entorno virtual en $($s.Nombre)..." -ForegroundColor DarkGray
        & $py -m venv $venv
    }

    $exe = Join-Path $venv "Scripts\python.exe"
    if (-not (Test-Path $exe)) { $exe = Join-Path $venv "bin\python" }

    Write-Host "Instalando dependencias de $($s.Nombre)..." -ForegroundColor DarkGray
    & $exe -m pip install --quiet --upgrade pip
    & $exe -m pip install --quiet -r (Join-Path $dir "requirements.txt")
}

# ---------------------------------------------------------------------------
Titulo "3/4  Iniciando las aplicaciones"

$procesos = @()

foreach ($s in $servicios) {
    $dir = Join-Path $raiz $s.Carpeta
    $exe = Join-Path $dir ".venv\Scripts\python.exe"

    Write-Host "  -> $($s.Nombre)" -ForegroundColor Green
    $p = Start-Process -FilePath $exe `
        -ArgumentList "app.py" `
        -WorkingDirectory $dir `
        -PassThru `
        -WindowStyle Minimized
    $procesos += $p
}

# ---------------------------------------------------------------------------
Titulo "4/4  Esperando a que respondan"

$puertos = @{ "Comercial" = 5001; "Inventario" = 5000 }
$ok = @{}

foreach ($nombre in $puertos.Keys) {
    $puerto = $puertos[$nombre]
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:$puerto/health" -TimeoutSec 3 -ErrorAction Stop
            if ($r.StatusCode -eq 200) { $ok[$nombre] = $true; break }
        } catch { }
        Start-Sleep -Seconds 2
    }
}

Write-Host ""
if ($ok["Comercial"])  { Write-Host "  Comercial  ACTIVO   http://localhost:5001" -ForegroundColor Green }
else { Write-Host "  Comercial  NO RESPONDE" -ForegroundColor Red }
if ($ok["Inventario"]) { Write-Host "  Inventario ACTIVO   http://localhost:5000" -ForegroundColor Green }
else { Write-Host "  Inventario NO RESPONDE" -ForegroundColor Red }

Write-Host ""
Write-Host "  ACCESOS" -ForegroundColor Cyan
Write-Host "  Comercial   http://localhost:5001/login   admin@admin.com / admin123"
Write-Host "  Vendedor    http://localhost:5001/login   vendedor@libreria.com / vendedor123"
Write-Host "  Inventario  http://localhost:5000/login   admin@admin.com / admin123"
Write-Host "  Tablero KPI http://localhost:5000/kpis"
Write-Host "  Portada     http://localhost:5000/portada"
Write-Host "  phpMyAdmin  http://localhost:8080          root / rootpass"
Write-Host ""
Write-Host "  Para detener las apps: cierran las ventanas,o Ctrl+C." -ForegroundColor DarkGray
Write-Host "  (puedes cerrar esta ventana: las apps siguen corriendo)" -ForegroundColor DarkGray

if (-not ($ok["Comercial"] -and $ok["Inventario"])) {
    Write-Host ""
    Write-Host "  Revisa los logs ejecutando cada app por separado:" -ForegroundColor Yellow
    Write-Host "    cd 'Comercial'; .\.venv\Scripts\python.exe app.py" -ForegroundColor Yellow
    Write-Host "    cd 'Inventario y gestion interna'; .\.venv\Scripts\python.exe app.py" -ForegroundColor Yellow
}
