<#
.SYNOPSIS
    Para o coletor de eventos e os containers deste projeto, preservando todos os dados.

.DESCRIPTION
    Não remove containers, volumes, índices nem arquivos de runtime\.
    -SomenteColetor para apenas o coletor e mantém Elasticsearch, Logstash e Kibana no ar.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\scripts\parar_demo.ps1
#>
[CmdletBinding()]
param(
    [switch] $SomenteColetor
)

$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent $PSScriptRoot
$PastaEstado = Join-Path $Raiz 'runtime\state'
$ArqPid = Join-Path $PastaEstado 'coletor.pid'
$ArqParar = Join-Path $PastaEstado 'parar.sinal'

function Passo([string] $Texto) { Write-Host "`n==> $Texto" -ForegroundColor Cyan }
function Ok([string] $Texto) { Write-Host "    OK     $Texto" -ForegroundColor Green }
function Aviso([string] $Texto) { Write-Host "    AVISO  $Texto" -ForegroundColor Yellow }

function Obter-NomeMutex {
    # Mesmo nome usado por coletar_eventos.ps1 (um coletor por cópia do projeto).
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Raiz.ToLowerInvariant()))
    $hex = -join ($bytes | ForEach-Object { $_.ToString('x2') })
    return 'Local\SeminarioKibana-Coletor-' + $hex.Substring(0, 16)
}

function Coletor-EmExecucao {
    $mutex = $null
    if ([System.Threading.Mutex]::TryOpenExisting((Obter-NomeMutex), [ref] $mutex)) { $mutex.Dispose(); return $true }
    return $false
}

Set-Location $Raiz

Passo 'Coletor de eventos'
if (-not (Coletor-EmExecucao)) {
    Ok 'O coletor não estava em execução.'
}
else {
    New-Item -ItemType Directory -Force -Path $PastaEstado | Out-Null
    New-Item -ItemType File -Force -Path $ArqParar | Out-Null
    $limite = (Get-Date).AddSeconds(30)
    while ((Coletor-EmExecucao) -and (Get-Date) -lt $limite) { Start-Sleep -Seconds 1 }
    if (-not (Coletor-EmExecucao)) {
        Ok 'Coletor encerrado (checkpoint salvo).'
    }
    else {
        # Último recurso: encerra o processo registrado, apenas se for mesmo o coletor deste projeto.
        $pidColetor = if (Test-Path $ArqPid) { [int] (Get-Content -Raw -Path $ArqPid).Trim() } else { 0 }
        $processo = Get-CimInstance Win32_Process -Filter "ProcessId = $pidColetor" -ErrorAction SilentlyContinue
        if ($processo -and $processo.CommandLine -like '*coletar_eventos.ps1*') {
            Stop-Process -Id $pidColetor -Force
            Aviso "O coletor não respondeu ao sinal e foi encerrado à força (PID $pidColetor)."
        }
        else {
            Aviso 'O coletor ainda parece ativo, mas o processo não foi identificado com segurança; nada foi encerrado à força.'
        }
    }
}

if ($SomenteColetor) {
    Write-Host "`nContainers mantidos em execução (opção -SomenteColetor)."
    exit 0
}

Passo 'Containers: Elasticsearch, Logstash e Kibana'
# Saída de erro do docker não deve interromper o script (Windows PowerShell 5.1); vale o código de saída.
$ErrorActionPreference = 'Continue'
docker compose stop
if ($LASTEXITCODE -eq 0) { Ok 'Containers parados. Dados preservados (volume do Elasticsearch e pasta runtime\).' }
else { Aviso 'Não foi possível parar os containers (o Docker está em execução?).' }
