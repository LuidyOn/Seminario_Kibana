<#
.SYNOPSIS
    Coleta eventos do canal Application do Windows e grava apenas metadados
    em JSON Lines (runtime/logs/eventos.jsonl), arquivo lido pelo Logstash.

.DESCRIPTION
    Primeira execução: amostra inicial com os eventos dos últimos dias (limitada).
    Depois: a cada intervalo, lê somente eventos com RecordId maior que o último
    exportado. O checkpoint fica em runtime/state/checkpoint.json.

    Campos exportados: horário (UTC), canal, provedor, ID do evento, RecordId,
    nível normalizado e um identificador aleatório desta instalação.
    A mensagem do evento e dados de usuário, processo ou computador NÃO são exportados.

    Normalmente é iniciado e parado por iniciar_demo.ps1 e parar_demo.ps1.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\scripts\coletar_eventos.ps1 -UmaVez
#>
[CmdletBinding()]
param(
    [ValidateRange(5, 3600)]
    [int] $IntervaloSegundos = 15,
    [ValidateRange(1, 365)]
    [int] $DiasIniciais = 7,
    [ValidateRange(1, 100000)]
    [int] $MaxInicial = 2000,
    # Faz uma única leitura e encerra (útil para testes).
    [switch] $UmaVez
)

$ErrorActionPreference = 'Stop'

$Canal = 'Application'
$Raiz = Split-Path -Parent $PSScriptRoot
$PastaLogs = Join-Path $Raiz 'runtime\logs'
$PastaEstado = Join-Path $Raiz 'runtime\state'
$ArqEventos = Join-Path $PastaLogs 'eventos.jsonl'
$ArqCheckpoint = Join-Path $PastaEstado 'checkpoint.json'
$ArqOrigem = Join-Path $PastaEstado 'origem.txt'
$ArqPid = Join-Path $PastaEstado 'coletor.pid'
$ArqParar = Join-Path $PastaEstado 'parar.sinal'
$ArqLog = Join-Path $PastaEstado 'coletor.log'
$Utf8SemBom = New-Object System.Text.UTF8Encoding($false)
$Invariante = [System.Globalization.CultureInfo]::InvariantCulture

function Registrar([string] $Texto) {
    $linha = '{0}  {1}' -f (Get-Date).ToString('yyyy-MM-dd HH:mm:ss'), $Texto
    [System.IO.File]::AppendAllText($ArqLog, $linha + "`n", $Utf8SemBom)
    Write-Host $linha
}

function Obter-NomeMutex {
    # Um coletor por cópia do projeto: o nome deriva do caminho da pasta raiz.
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Raiz.ToLowerInvariant()))
    $hex = -join ($bytes | ForEach-Object { $_.ToString('x2') })
    return 'Local\SeminarioKibana-Coletor-' + $hex.Substring(0, 16)
}

function Obter-Origem {
    # Identificador aleatório gerado uma vez por instalação; não deriva do nome do PC nem do usuário.
    if (Test-Path $ArqOrigem) {
        $valor = (Get-Content -Raw -Path $ArqOrigem).Trim()
        if ($valor) { return $valor }
    }
    $valor = 'pc-' + [guid]::NewGuid().ToString('N').Substring(0, 12)
    [System.IO.File]::WriteAllText($ArqOrigem, $valor, $Utf8SemBom)
    return $valor
}

function Converter-Nivel($Level) {
    # Valores do enum StandardEventLevel; o nível 0 (LogAlways) aparece como "Informações" no Visualizador de Eventos.
    if ($null -eq $Level) { return 'Unknown' }
    switch ([int] $Level) {
        0 { return 'Information' }
        1 { return 'Critical' }
        2 { return 'Error' }
        3 { return 'Warning' }
        4 { return 'Information' }
        5 { return 'Verbose' }
        default { return "Level $Level" }
    }
}

function Converter-Evento($Evento, [string] $Origem) {
    if ($null -eq $Evento.TimeCreated -or $null -eq $Evento.RecordId) { return $null }
    $utc = $Evento.TimeCreated.ToUniversalTime()
    $documento = [ordered]@{
        '@timestamp' = $utc.ToString("yyyy-MM-dd'T'HH:mm:ss.fff'Z'", $Invariante)
        event        = [ordered]@{
            # ID estável: o mesmo evento sempre gera o mesmo documento no Elasticsearch.
            id       = '{0}-{1}-{2}' -f $Canal, $Evento.RecordId, $utc.ToString('yyyyMMddHHmmssfff', $Invariante)
            code     = [string] $Evento.Id
            provider = [string] $Evento.ProviderName
        }
        log          = [ordered]@{ level = (Converter-Nivel $Evento.Level) }
        winlog       = [ordered]@{ channel = [string] $Evento.LogName; record_id = [long] $Evento.RecordId }
        host         = [ordered]@{ id = $Origem }
    }
    return ($documento | ConvertTo-Json -Compress -Depth 4)
}

function Exportar([object[]] $Eventos, [string] $Origem) {
    $linhas = New-Object System.Collections.Generic.List[string]
    foreach ($evento in ($Eventos | Sort-Object RecordId)) {
        $linha = Converter-Evento $evento $Origem
        if ($linha) { $linhas.Add($linha) }
    }
    if ($linhas.Count -gt 0) {
        # Um único append por lote, sempre terminado em quebra de linha (JSON Lines, UTF-8 sem BOM).
        [System.IO.File]::AppendAllText($ArqEventos, (($linhas -join "`n") + "`n"), $Utf8SemBom)
    }
    return $linhas.Count
}

function Consultar([scriptblock] $Consulta) {
    # Get-WinEvent sinaliza "nenhum evento" com o erro NoMatchingEventsFound.
    try { return @(& $Consulta) }
    catch {
        if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') { return @() }
        throw
    }
}

function Obter-RecordIdExtremo([switch] $MaisAntigo) {
    $r = @(Consultar { Get-WinEvent -LogName $Canal -MaxEvents 1 -Oldest:$MaisAntigo -ErrorAction Stop })
    if ($r.Count -eq 0) { return $null }
    return [long] $r[0].RecordId
}

function Ler-Checkpoint {
    if (-not (Test-Path $ArqCheckpoint)) { return $null }
    try { return (Get-Content -Raw -Path $ArqCheckpoint -Encoding UTF8 | ConvertFrom-Json) }
    catch {
        Registrar "AVISO: checkpoint ilegível ($($_.Exception.Message)); será feita nova amostra inicial."
        return $null
    }
}

function Gravar-Checkpoint([long] $Ultimo, [string] $UltimoUtc, [long] $Total) {
    $estado = [ordered]@{
        canal              = $Canal
        ultimo_record_id   = $Ultimo
        ultimo_evento_utc  = $UltimoUtc
        eventos_exportados = $Total
        ultima_verificacao = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd'T'HH:mm:ss'Z'", $Invariante)
    }
    $temporario = "$ArqCheckpoint.tmp"
    [System.IO.File]::WriteAllText($temporario, ($estado | ConvertTo-Json), $Utf8SemBom)
    if (Test-Path $ArqCheckpoint) { [System.IO.File]::Replace($temporario, $ArqCheckpoint, [NullString]::Value) }
    else { [System.IO.File]::Move($temporario, $ArqCheckpoint) }
}

function Aguardar-Intervalo {
    # Dorme em passos de 1 s para atender rapidamente ao sinal de parada.
    for ($i = 0; $i -lt $IntervaloSegundos; $i++) {
        if (Test-Path $ArqParar) { return $true }
        Start-Sleep -Seconds 1
    }
    return (Test-Path $ArqParar)
}

New-Item -ItemType Directory -Force -Path $PastaLogs, $PastaEstado | Out-Null
$codigoSaida = 0

$mutex = New-Object System.Threading.Mutex($false, (Obter-NomeMutex))
$temMutex = $false
try { $temMutex = $mutex.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $temMutex = $true }
if (-not $temMutex) {
    Write-Host 'Já existe um coletor em execução para este projeto; nenhum outro foi iniciado.'
    exit 0
}

try {
    if (Test-Path $ArqParar) { Remove-Item -Force $ArqParar }
    [System.IO.File]::WriteAllText($ArqPid, [string] $PID, $Utf8SemBom)
    $origem = Obter-Origem
    Registrar "Coletor iniciado (PID $PID, canal $Canal, intervalo de $IntervaloSegundos s)."

    $checkpoint = Ler-Checkpoint
    $ultimo = [long] 0
    $ultimoUtc = ''
    $total = [long] 0
    if ($checkpoint) {
        $ultimo = [long] $checkpoint.ultimo_record_id
        $ultimoUtc = [string] $checkpoint.ultimo_evento_utc
        $total = [long] $checkpoint.eventos_exportados
        $maisNovo = Obter-RecordIdExtremo
        $maisAntigo = Obter-RecordIdExtremo -MaisAntigo
        if ($null -ne $maisNovo -and $maisNovo -lt $ultimo) {
            Registrar "AVISO: o maior RecordId atual ($maisNovo) é menor que o checkpoint ($ultimo): o log $Canal foi limpo ou recriado. Nova amostra inicial; documentos antigos continuam no índice."
            $checkpoint = $null
        }
        elseif ($null -ne $maisAntigo -and $maisAntigo -gt ($ultimo + 1)) {
            Registrar ('AVISO: {0} evento(s) (RecordId {1} a {2}) foram descartados pelo log circular do Windows antes de serem coletados.' -f ($maisAntigo - $ultimo - 1), ($ultimo + 1), ($maisAntigo - 1))
        }
        else {
            Registrar "Retomando após o RecordId $ultimo ($total evento(s) já exportados)."
        }
    }

    if (-not $checkpoint) {
        $inicio = (Get-Date).AddDays(-$DiasIniciais)
        $amostra = @(Consultar { Get-WinEvent -FilterHashtable @{ LogName = $Canal; StartTime = $inicio } -MaxEvents $MaxInicial -ErrorAction Stop })
        $n = Exportar $amostra $origem
        $total += $n
        if ($amostra.Count -gt 0) {
            $maisRecente = $amostra | Sort-Object RecordId | Select-Object -Last 1
            $ultimo = [long] $maisRecente.RecordId
            $ultimoUtc = $maisRecente.TimeCreated.ToUniversalTime().ToString("yyyy-MM-dd'T'HH:mm:ss'Z'", $Invariante)
        }
        else {
            $maisNovo = Obter-RecordIdExtremo
            if ($null -ne $maisNovo) { $ultimo = $maisNovo }
        }
        Gravar-Checkpoint $ultimo $ultimoUtc $total
        Registrar "Amostra inicial: $n evento(s) dos últimos $DiasIniciais dia(s) (limite de $MaxInicial)."
    }

    while ($true) {
        try {
            $novos = @(Consultar { Get-WinEvent -LogName $Canal -FilterXPath "*[System[EventRecordID > $ultimo]]" -ErrorAction Stop })
            if ($novos.Count -gt 0) {
                $n = Exportar $novos $origem
                $total += $n
                $maisRecente = $novos | Sort-Object RecordId | Select-Object -Last 1
                $ultimo = [long] $maisRecente.RecordId
                $ultimoUtc = $maisRecente.TimeCreated.ToUniversalTime().ToString("yyyy-MM-dd'T'HH:mm:ss'Z'", $Invariante)
                Registrar "$n evento(s) novo(s) exportado(s); último RecordId $ultimo."
            }
            else {
                $maisNovo = Obter-RecordIdExtremo
                if ($null -ne $maisNovo -and $maisNovo -lt $ultimo) {
                    Registrar "AVISO: o log $Canal foi limpo ou recriado (maior RecordId $maisNovo < checkpoint $ultimo). A coleta continua a partir do início do novo log."
                    $ultimo = 0
                }
            }
            Gravar-Checkpoint $ultimo $ultimoUtc $total
        }
        catch {
            Registrar "ERRO na leitura dos eventos: $($_.Exception.Message) (nova tentativa no próximo ciclo)."
            if ($UmaVez) { $codigoSaida = 1 }
        }
        if ($UmaVez) { break }
        if (Aguardar-Intervalo) { Registrar 'Sinal de parada recebido.'; break }
    }
}
catch {
    Registrar "ERRO fatal: $($_.Exception.Message)"
    exit 1
}
finally {
    if (Test-Path $ArqPid) { Remove-Item -Force $ArqPid }
    if (Test-Path $ArqParar) { Remove-Item -Force $ArqParar }
    Registrar 'Coletor encerrado.'
    $mutex.ReleaseMutex()
    $mutex.Dispose()
}
exit $codigoSaida
