# Roteiro da demonstração (≈ 5 minutos)

Demonstração ao vivo do fluxo **Windows Event Log → coletor PowerShell → `eventos.jsonl` → Logstash → Elasticsearch → Kibana (Discover, filtro, Lens, Dashboard)**, com eventos reais do computador da apresentação. Os nomes de botões estão em inglês porque a interface do Kibana está em inglês. Os comandos devem ser executados no PowerShell, na pasta do projeto.

## 1. Verificação no computador da apresentação

O fluxo foi validado no computador da apresentação. Se a máquina mudar, repita a verificação com antecedência.

1. Abra o Docker Desktop e confira se o Windows tem cerca de 3 GB de RAM disponíveis.
2. Execute `powershell -ExecutionPolicy Bypass -File .\iniciar.ps1` e confira as seis etapas. Compare a contagem do índice com os IDs únicos do arquivo do coletor após o Logstash terminar a leitura. Releituras podem repetir linhas no arquivo.
3. `docker compose ps`: `elasticsearch` e `kibana` como `healthy` e `logstash` em execução. Em `docker compose logs --tail 30 logstash`, o pipeline `main` deve aparecer iniciado e sem erros.
4. Abra o [dashboard Eventos do Windows](http://localhost:5601/app/dashboards#/view/eventos-windows). Confira os quatro painéis em **Last 7 days** e compare o total com o **Discover** no mesmo intervalo. O endpoint `/windows-events/_count` conta todos os documentos do índice.
5. Para testar a retomada, rode `powershell -ExecutionPolicy Bypass -File .\scripts\parar_demo.ps1` e repita o comando de início. O total no índice cresce à medida que novos eventos são coletados.
6. Anote o consumo com `docker stats --no-stream`. Se o Logstash registrar `OutOfMemoryError`, aumente `LS_JAVA_OPTS` para `-Xms512m -Xmx512m` no `docker-compose.yml`.

## 2. Preparação

### Na véspera (≈ 20 min)

1. Siga a seção 1, se ainda não tiver sido feita.
2. No Kibana, no aviso *Your data is not secure*, marque **Don't show again** e clique em **Dismiss**. O aviso existe porque a segurança foi desligada de propósito; vale citá-lo na parte de limitações.
3. Faça um ensaio completo da seção 3, cronometrando e gravando a tela: essa gravação é o vídeo de contingência (seção 6).
4. Para restaurar os quatro painéis originais após o ensaio, rode `powershell -ExecutionPolicy Bypass -File .\iniciar.ps1 -RestaurarDashboard`.

### 30 minutos antes

- Feche programas pesados, silencie notificações e abra o Docker Desktop.
- Rode `powershell -ExecutionPolicy Bypass -File .\iniciar.ps1` e aguarde a conclusão.
- **Pare só o coletor:** `powershell -ExecutionPolicy Bypass -File .\scripts\parar_demo.ps1 -SomenteColetor`. Assim, os eventos que o Windows registrar até a demonstração ficam "pendentes" e serão importados ao vivo (no computador de testes, o canal Aplicativo registrou cerca de 25 eventos por hora).
- Deixe abertos:
  - o **Visualizador de Eventos** (`eventvwr.msc`) → Logs do Windows → Aplicativo, com o painel de visualização da mensagem **oculto** (menu Exibir), para não exibir mensagens que podem conter dados pessoais;
  - um terminal PowerShell na pasta do projeto;
  - o arquivo `logstash/pipeline/windows-events.conf` num editor;
  - o Kibana na Home, com zoom do navegador em 125%.

## 3. Roteiro cronometrado

| Tempo | Ação | Fala de apoio |
|---|---|---|
| 00:00 | Visualizador de Eventos → Aplicativo | "Esta é a fonte dos eventos. A coleta usa metadados como nível, data e hora, fonte e ID." |
| 00:40 | `powershell -ExecutionPolicy Bypass -File .\iniciar.ps1` | "O script confere o Docker e os containers e retoma a coleta." |
| 01:10 | `Get-Content runtime\state\coletor.log -Tail 3` e `Get-Content runtime\logs\eventos.jsonl -Tail 1` | "O coletor importou os eventos que já existiam no Windows enquanto estava parado. Cada evento vira uma linha JSON." Se não houver eventos novos, dizer que a verificação continua a cada 15 s; não forçar eventos. |
| 01:50 | Mostrar `windows-events.conf` | "O Logstash é configurado assim: entrada `file` com codec `json`, um filtro que limpa campos técnicos e saída para o Elasticsearch, com ID estável para não duplicar." |
| 02:20 | Navegador: <http://localhost:9200/windows-events/_count> | "O Elasticsearch já tem os documentos reais indexados." |
| 02:40 | Kibana → **Menu → Analytics → Discover**. Selecione **Data view → Eventos do Windows** e o intervalo **Last 7 days** (ou **Search entire time range**). | "Os eventos mais recentes aparecem no topo." Mostrar os campos de interesse. |
| 03:10 | Barra de busca: `log.level : "Error"` + Enter (ou `"Warning"`, conforme o que existir no computador) | "Com a KQL, isolamos só os erros." |
| 03:40 | Apagar a busca → prévia de `event.code` → **Visualize** → **Save** → *Title* `IDs de evento mais frequentes` → **Existing** → *Eventos do Windows* → **Save and go to dashboard**. Clique em **Save** e, se necessário, em **Exit edit**. | "O Lens montou o gráfico a partir de um campo e podemos incluí-lo no dashboard." |
| 04:30 | Clique em uma barra de **Eventos por nível** e confira o filtro `log.level`. No menu do botão direito, a ação equivalente é **Filter for** seguido do nível. | "Um clique filtra todos os painéis. O dashboard também se atualiza a cada 30 segundos." |
| 05:00 | Encerrar e voltar aos slides | "Windows, coletor, Logstash, Elasticsearch e Kibana: o fluxo completo, com dados reais." |

Os totais, níveis e provedores variam conforme o computador e o intervalo. Para desfazer o filtro do clique, remova-o no **×**. Use `-RestaurarDashboard` após um ensaio em que você tenha salvo o gráfico adicional.

## 4. Diagnóstico rápido

| Comando | O que mostra |
|---|---|
| `docker compose ps` | Estado dos containers (`healthy` para Elasticsearch e Kibana) |
| `docker compose logs --tail 50 logstash` | Leitura do arquivo e envio ao Elasticsearch; linhas inválidas aparecem aqui |
| `curl.exe http://localhost:9200/windows-events/_count` | Quantidade de eventos no índice |
| `Get-Content runtime\state\coletor.log -Tail 20` | Atividade do coletor, avisos e erros |
| `Get-Content runtime\state\checkpoint.json` | Último `RecordId` exportado e horário da última verificação |
| `docker stats --no-stream` | Memória usada por container |

O log do Kibana registra avisos de recursos que a demonstração não usa (Fleet, Cloud Connect, telemetria) e, às vezes, erros genéricos `500 Server Error`; nos testes anteriores, nenhum deles afetou as telas usadas.

## 5. Problemas comuns

| Sintoma | Ação |
|---|---|
| "A execução de scripts foi desabilitada neste sistema" | Rode `powershell -ExecutionPolicy Bypass -File .\iniciar.ps1`. A opção vale para esse processo do PowerShell. |
| "O Docker Engine não respondeu" | Abrir o Docker Desktop, esperar *Engine running* e rodar o script de novo. |
| Contagem do índice fica em 0 | Ver `docker compose logs --tail 50 logstash` e o `coletor.log`; conferir se `runtime\logs\eventos.jsonl` existe. |
| Índice com menos eventos que o arquivo | O Logstash ainda está lendo (aguardar) ou o arquivo tem linhas repetidas após uma falha (normal: o índice não duplica). |
| Dashboard vazio | Conferir o intervalo de tempo (Last 7 days) e a contagem do índice. |
| "Kibana server is not ready yet" | Aguardar até 4 minutos; conferir memória livre. |
| Tudo lento ou container parado com `Exited (137)` | Falta de memória: fechar programas. No Windows, a memória da VM do Docker pode ser aumentada em `%UserProfile%\.wslconfig` (seção `[wsl2]`, `memory=6GB`, seguido de `wsl --shutdown`). |
| `OutOfMemoryError` no Logstash ou no Elasticsearch | Aumentar `LS_JAVA_OPTS` para 512m ou `ES_JAVA_OPTS` para 1g no `docker-compose.yml` e rodar o script de início. |
| Aviso de log limpo ou de eventos descartados no `coletor.log` | Informativo: o coletor recomeçou ou registrou a lacuna; nada a corrigir. |

**Regra prática:** se um problema não for resolvido em cerca de 1 minuto durante a apresentação, passar para a contingência.

## 6. Contingência: gravação prévia

A avaliação aceita gravação apenas como contingência em caso de dificuldade técnica justificada:

- **Quando gravar:** na véspera, durante o ensaio (seção 2), seguindo a seção 3 (≈ 5 minutos).
- **Como gravar:** no Windows, Xbox Game Bar (**Win + Alt + R** inicia e para a gravação) ou OBS Studio. Resolução 1920×1080, zoom de 125%, notificações desligadas e, de preferência, sem áudio, para narrar ao vivo. Não mostrar mensagens de eventos nem dados pessoais.
- **Onde guardar:** no computador da apresentação, para tocar sem internet, e uma cópia em pendrive. Testar a reprodução antes da aula.
- **Como usar:** explicar brevemente a dificuldade técnica, reproduzir o vídeo e narrar os pontos da coluna "Fala de apoio".
