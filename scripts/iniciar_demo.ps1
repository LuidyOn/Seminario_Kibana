<#
.SYNOPSIS
    Sobe a demonstração: Elasticsearch, Logstash e Kibana (Docker) e o coletor de eventos do Windows.

.DESCRIPTION
    Pode ser executado mais de uma vez: não duplica o coletor e não apaga dados.
    O dashboard é importado no Kibana se ainda não existir; -RestaurarDashboard
    volta o dashboard à versão original do repositório.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\scripts\iniciar_demo.ps1
#>
[CmdletBinding()]
param(
    [switch] $RestaurarDashboard
)

$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent $PSScriptRoot
$PastaEstado = Join-Path $Raiz 'runtime\state'
$ArqEventos = Join-Path $Raiz 'runtime\logs\eventos.jsonl'
$ArqLogColetor = Join-Path $PastaEstado 'coletor.log'
$Coletor = Join-Path $PSScriptRoot 'coletar_eventos.ps1'
$Dashboard = Join-Path $Raiz 'kibana\dashboard_eventos.ndjson'

function Passo([string] $Texto) { Write-Host "`n==> $Texto" -ForegroundColor Cyan }
function Ok([string] $Texto) { Write-Host "    OK     $Texto" -ForegroundColor Green }
function Aviso([string] $Texto) { Write-Host "    AVISO  $Texto" -ForegroundColor Yellow }
function Falhar([string] $Texto) { Write-Host "`nERRO: $Texto" -ForegroundColor Red; exit 1 }

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

function Aguardar([scriptblock] $Condicao, [int] $Segundos) {
    $limite = (Get-Date).AddSeconds($Segundos)
    while ((Get-Date) -lt $limite) {
        try { if (& $Condicao) { return $true } } catch { }
        Start-Sleep -Seconds 3
    }
    return $false
}

function Nativo([scriptblock] $Comando, [switch] $Silencioso) {
    # No Windows PowerShell 5.1, a saída de erro de programas externos não deve interromper o script:
    # o resultado é avaliado pelo código de saída.
    $ErrorActionPreference = 'Continue'
    if ($Silencioso) { & $Comando *> $null } else { & $Comando | Out-Host }
    return $LASTEXITCODE
}

function Docker-Disponivel {
    return ((Nativo { docker info --format '{{.ServerVersion}}' } -Silencioso) -eq 0)
}

Set-Location $Raiz

Passo '1/6 Pré-requisitos'
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Falhar 'Docker não encontrado. Instale o Docker Desktop e tente novamente.' }
if ((Nativo { docker compose version } -Silencioso) -ne 0) { Falhar 'Docker Compose v2 não encontrado (comando "docker compose").' }
if (-not (Docker-Disponivel)) {
    Aviso 'Docker Engine parado; tentando iniciar o Docker Desktop...'
    Nativo { docker desktop start } -Silencioso | Out-Null
    if (-not (Aguardar { Docker-Disponivel } 180)) {
        Falhar 'O Docker Engine não respondeu. Abra o Docker Desktop, aguarde "Engine running" e rode este script de novo.'
    }
}
Ok 'Docker Engine em execução.'
# Verificação apenas informativa: se o contador de memória não estiver disponível, segue sem ela.
$memoria = try { (Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory).AvailableMBytes } catch { $null }
if ($null -eq $memoria) {
    Aviso 'Não foi possível medir a RAM livre. A demonstração usa cerca de 3 GB.'
}
elseif ($memoria -lt 3500) {
    Aviso "Apenas $memoria MB de RAM livres. A demonstração usa cerca de 3 GB: feche outros programas se o computador ficar lento."
}
else { Ok "$memoria MB de RAM livres." }

Passo '2/6 Pastas locais de execução (runtime\, fora do Git)'
New-Item -ItemType Directory -Force -Path (Join-Path $Raiz 'runtime\logs'), (Join-Path $PastaEstado 'logstash') | Out-Null
Ok (Join-Path $Raiz 'runtime')

Passo '3/6 Containers: Elasticsearch, Logstash e Kibana (pode levar alguns minutos)'
if ((Nativo { docker compose up -d --wait --wait-timeout 420 }) -ne 0) {
    Falhar 'Os containers não ficaram prontos. Veja "docker compose ps" e "docker compose logs --tail 50".'
}
Ok 'Containers prontos.'

Passo '4/6 Coletor de eventos do Windows (canal Application)'
if (Coletor-EmExecucao) {
    Ok 'O coletor já estava em execução; nenhum outro foi iniciado.'
}
else {
    $sinal = Join-Path $PastaEstado 'parar.sinal'
    if (Test-Path $sinal) { Remove-Item -Force $sinal }
    $argumentos = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}"' -f $Coletor
    Start-Process -FilePath 'powershell.exe' -ArgumentList $argumentos -WindowStyle Hidden | Out-Null
    if (-not (Aguardar { Coletor-EmExecucao } 30)) { Falhar "O coletor não iniciou. Veja $ArqLogColetor." }
    Ok 'Coletor iniciado em segundo plano (verifica novos eventos a cada 15 s).'
}

Passo '5/6 Dashboard no Kibana'
$limite = [guid]::NewGuid().ToString('N')
$ndjson = [System.IO.File]::ReadAllText($Dashboard, [System.Text.Encoding]::UTF8)
$corpo = "--$limite`r`nContent-Disposition: form-data; name=`"file`"; filename=`"dashboard_eventos.ndjson`"`r`nContent-Type: application/ndjson`r`n`r`n$ndjson`r`n--$limite--`r`n"
$sobrescrever = if ($RestaurarDashboard) { 'true' } else { 'false' }
$resposta = Invoke-RestMethod -Method Post -Uri "http://localhost:5601/api/saved_objects/_import?overwrite=$sobrescrever" `
    -Headers @{ 'kbn-xsrf' = 'true' } -ContentType "multipart/form-data; boundary=$limite" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($corpo))
$conflitos = @($resposta.errors | Where-Object { $_.error.type -eq 'conflict' }).Count
$outrosErros = @($resposta.errors | Where-Object { $_.error.type -ne 'conflict' }).Count
if ($outrosErros -gt 0) { Falhar "A importação do dashboard falhou: $($resposta.errors | ConvertTo-Json -Depth 5 -Compress)" }
if ($resposta.successCount -gt 0) { Ok "$($resposta.successCount) objeto(s) importado(s) (Data View, visualizações e dashboard)." }
if ($conflitos -gt 0) { Ok "$conflitos objeto(s) já existiam e foram mantidos (use -RestaurarDashboard para voltar ao original)." }

Passo '6/6 Conferência: eventos chegando ao Elasticsearch'
$contar = { (Invoke-RestMethod -Uri 'http://localhost:9200/windows-events/_count').count -gt 0 }
if (-not (Aguardar $contar 180)) {
    Falhar 'Nenhum evento chegou ao índice windows-events. Veja "docker compose logs --tail 50 logstash" e o log do coletor.'
}
$noIndice = (Invoke-RestMethod -Uri 'http://localhost:9200/windows-events/_count').count
$noArquivo = if (Test-Path $ArqEventos) { @(Get-Content -Path $ArqEventos).Count } else { 0 }
Ok "$noIndice evento(s) no índice windows-events ($noArquivo linha(s) no arquivo do coletor)."
if (Test-Path $ArqLogColetor) { Write-Host ('    Coletor: ' + (Get-Content -Path $ArqLogColetor -Encoding UTF8 -Tail 1)) }

Write-Host "`nPronto. Abra http://localhost:5601 -> Dashboards -> 'Eventos do Windows'." -ForegroundColor Green
Write-Host 'Para encerrar: powershell -ExecutionPolicy Bypass -File .\scripts\parar_demo.ps1'
