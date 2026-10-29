# Roteiro da demonstração (≈ 5 minutos)

Demonstração ao vivo do fluxo **Windows Event Log → coletor PowerShell → `eventos.jsonl` → Logstash → Elasticsearch → Kibana (Discover, filtro, Lens, Dashboard)**, com eventos reais do computador da apresentação. Os nomes de botões estão em inglês porque a interface do Kibana está em inglês. Os comandos devem ser executados no PowerShell, na pasta do projeto.

## 1. Primeira validação no computador da apresentação (obrigatória)

O coletor foi validado no computador de desenvolvimento, mas o fluxo completo com Logstash, Elasticsearch e Kibana ainda **não foi executado de ponta a ponta** (faltou memória livre naquele computador). Faça esta verificação uma vez, com antecedência, no computador que será usado no seminário:

1. Feche programas pesados (o ambiente precisa de cerca de 3 GB de RAM) e abra o Docker Desktop.
2. Execute `powershell -ExecutionPolicy Bypass -File .\scripts\iniciar_demo.ps1` e confira as 6 etapas com **OK**. A última mostra quantos eventos estão no índice e quantas linhas há no arquivo do coletor; depois que o Logstash termina a leitura, os dois números devem coincidir (o arquivo pode ter linhas a mais se houver releitura após falhas, nunca a menos).
3. `docker compose ps`: `elasticsearch` e `kibana` como `healthy` e `logstash` em execução. Em `docker compose logs --tail 30 logstash`, o pipeline `main` deve aparecer iniciado e sem erros.
4. Abra <http://localhost:5601> → **Explore on my own** → **Dashboards** → **Eventos do Windows**: os quatro painéis devem aparecer sem erro, e o total deve bater com `curl.exe http://localhost:9200/windows-events/_count`.
5. Teste de retomada: rode `parar_demo.ps1` e depois `iniciar_demo.ps1` de novo. O total no índice só pode crescer pelos eventos realmente novos do Windows, nunca por duplicação.
6. Anote o consumo com `docker stats --no-stream`. Se o Logstash registrar `OutOfMemoryError`, aumente `LS_JAVA_OPTS` para `-Xms512m -Xmx512m` no `docker-compose.yml`.
7. Registre o resultado no README (seção "Validação"), corrija qualquer passo deste roteiro que tenha se comportado diferente e, se tudo funcionar, remova os arquivos da versão anterior listados ali.

## 2. Preparação

### Na véspera (≈ 20 min)

1. Siga a seção 1, se ainda não tiver sido feita.
2. No Kibana, no aviso *Your data is not secure*, marque **Don't show again** e clique em **Dismiss**. O aviso existe porque a segurança foi desligada de propósito; vale citá-lo na parte de limitações.
3. Faça um ensaio completo da seção 3, cronometrando e gravando a tela: essa gravação é o vídeo de contingência (seção 6).
4. Para voltar o dashboard ao estado original depois do ensaio: `powershell -ExecutionPolicy Bypass -File .\scripts\iniciar_demo.ps1 -RestaurarDashboard`.

### 30 minutos antes

- Feche programas pesados, silencie notificações e abra o Docker Desktop.
- Rode `iniciar_demo.ps1` e espere as 6 etapas com OK.
- **Pare só o coletor:** `powershell -ExecutionPolicy Bypass -File .\scripts\parar_demo.ps1 -SomenteColetor`. Assim, os eventos que o Windows registrar até a demonstração ficam "pendentes" e serão importados ao vivo (no computador de testes, o canal Aplicativo registrou cerca de 25 eventos por hora).
- Deixe abertos:
  - o **Visualizador de Eventos** (`eventvwr.msc`) → Logs do Windows → Aplicativo, com o painel de visualização da mensagem **oculto** (menu Exibir), para não exibir mensagens que podem conter dados pessoais;
  - um terminal PowerShell na pasta do projeto;
  - o arquivo `logstash/pipeline/windows-events.conf` num editor;
  - o Kibana na Home, com zoom do navegador em 125%.

## 3. Roteiro cronometrado

| Tempo | Ação | Fala de apoio |
|---|---|---|
| 00:00 | Visualizador de Eventos → Aplicativo | "Esta é a fonte real: cada linha é um evento, com nível, data e hora, fonte e ID. Só esses metadados saem do computador; a mensagem não." |
| 00:40 | Terminal: `powershell -ExecutionPolicy Bypass -File .\scripts\iniciar_demo.ps1` | "O script confere o Docker, os containers e religa o coletor." |
| 01:10 | `Get-Content runtime\state\coletor.log -Tail 3` e `Get-Content runtime\logs\eventos.jsonl -Tail 1` | "O coletor importou os eventos que já existiam no Windows enquanto estava parado. Cada evento vira uma linha JSON." Se não houver eventos novos, dizer que a verificação continua a cada 15 s; não forçar eventos. |
| 01:50 | Mostrar `windows-events.conf` | "O Logstash é configurado assim: entrada `file` com codec `json`, um filtro que limpa campos técnicos e saída para o Elasticsearch, com ID estável para não duplicar." |
| 02:20 | Navegador: <http://localhost:9200/windows-events/_count> | "O Elasticsearch já tem os documentos reais indexados." |
| 02:40 | Kibana: **Discover** → Data View **Eventos do Windows** → intervalo **Last 7 days** (ou **Search entire time range**) | "Os eventos mais recentes aparecem no topo." Abrir um documento e mostrar os campos. |
| 03:10 | Barra de busca: `log.level : "Error"` + Enter (ou `"Warning"`, conforme o que existir no computador) | "Com a KQL, isolamos só os erros." |
| 03:40 | Apagar a busca → campo `event.code` → **Visualize** → **Save** → *Title*: `IDs de evento mais frequentes` → **Existing** → *Eventos do Windows* → **Save and go to dashboard** → **Save** → **Exit edit** | "O Lens montou o gráfico a partir de um campo, e ele entra no dashboard." |
| 04:30 | No dashboard, clicar em uma barra de **Eventos por nível** → **Apply** | "Um clique filtra todos os painéis. O dashboard também se atualiza sozinho a cada 30 segundos." |
| 05:00 | Encerrar e voltar aos slides | "Windows, coletor, Logstash, Elasticsearch e Kibana: o fluxo completo, com dados reais." |

Os valores (total, níveis, provedores) dependem do computador e do momento; não há números fixos a decorar. Para desfazer o filtro do clique, remova-o no **x** e reabra o dashboard.

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
| "A execução de scripts foi desabilitada neste sistema" | Usar sempre `powershell -ExecutionPolicy Bypass -File .\scripts\<script>.ps1` (vale só para aquele comando). |
| "O Docker Engine não respondeu" | Abrir o Docker Desktop, esperar *Engine running* e rodar o script de novo. |
| Contagem do índice fica em 0 | Ver `docker compose logs --tail 50 logstash` e o `coletor.log`; conferir se `runtime\logs\eventos.jsonl` existe. |
| Índice com menos eventos que o arquivo | O Logstash ainda está lendo (aguardar) ou o arquivo tem linhas repetidas após uma falha (normal: o índice não duplica). |
| Dashboard vazio | Conferir o intervalo de tempo (Last 7 days) e a contagem do índice. |
| "Kibana server is not ready yet" | Aguardar até 4 minutos; conferir memória livre. |
| Tudo lento ou container parado com `Exited (137)` | Falta de memória: fechar programas. No Windows, a memória da VM do Docker pode ser aumentada em `%UserProfile%\.wslconfig` (seção `[wsl2]`, `memory=6GB`, seguido de `wsl --shutdown`). |
| `OutOfMemoryError` no Logstash ou no Elasticsearch | Aumentar `LS_JAVA_OPTS` para 512m ou `ES_JAVA_OPTS` para 1g no `docker-compose.yml` e rodar o script de início. |
| Aviso de log limpo ou de eventos descartados no `coletor.log` | Informativo: o coletor recomeçou ou registrou a lacuna; nada a corrigir. |

**Último recurso (apaga dados):** `docker compose down -v` remove o índice e os objetos do Kibana; apague também a pasta `runtime\` para coletar tudo de novo e rode o script de início (≈ 5 minutos). Não usar durante a apresentação.

**Regra prática:** se um problema não for resolvido em cerca de 1 minuto durante a apresentação, passar para a contingência.

## 6. Contingência: gravação prévia

A avaliação aceita gravação apenas como contingência em caso de dificuldade técnica justificada:

- **Quando gravar:** na véspera, durante o ensaio (seção 2), seguindo a seção 3 (≈ 5 minutos).
- **Como gravar:** no Windows, Xbox Game Bar (**Win + Alt + R** inicia e para a gravação) ou OBS Studio. Resolução 1920×1080, zoom de 125%, notificações desligadas e, de preferência, sem áudio, para narrar ao vivo. Não mostrar mensagens de eventos nem dados pessoais.
- **Onde guardar:** no computador da apresentação, para tocar sem internet, e uma cópia em pendrive. Testar a reprodução antes da aula.
- **Como usar:** explicar brevemente a dificuldade técnica, reproduzir o vídeo e narrar os pontos da coluna "Fala de apoio".
