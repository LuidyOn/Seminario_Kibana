# Roteiro da demonstração (≈ 5 minutos)

Demonstração ao vivo do fluxo **CSV → Elasticsearch → Kibana (Discover, filtro, Lens, Dashboard)**. Os nomes de botões estão em inglês porque a interface do Kibana está em inglês; todos foram conferidos no Kibana 9.5.5.

## 1. Preparação

### Na véspera (≈ 20 min)

1. Com internet, subir o ambiente: `docker compose up -d` (a primeira vez baixa as imagens, cerca de 5 GB).
2. Conferir: `docker compose ps` deve mostrar os dois serviços como `healthy`.
3. Abrir <http://localhost:5601> e clicar em **Explore on my own**.
4. Importar o dashboard: busca do topo → **Saved objects** → **Import** → `kibana/dashboard_acessos.ndjson` → **Import** → **Done** (deve aparecer "6 objects imported").
5. No aviso *Your data is not secure*, marcar **Don't show again** e clicar em **Dismiss**. O aviso existe porque a segurança foi desligada de propósito; vale citá-lo na parte de limitações.
6. Fazer um ensaio completo seguindo a seção 2, cronometrando e gravando a tela: essa gravação é o vídeo de contingência (seção 6).
7. Voltar ao estado inicial para a apresentação:
   - apagar o índice criado no ensaio: `curl -X DELETE http://localhost:9200/acessos` (PowerShell: `curl.exe -X DELETE http://localhost:9200/acessos`);
   - reimportar `kibana/dashboard_acessos.ndjson` (passo 4) para descartar o painel salvo no ensaio.

### 30 minutos antes

- Fechar programas pesados e silenciar notificações. O ambiente precisa de cerca de 3 GB de RAM e, no Windows, a VM do Docker (WSL 2) usa por padrão no máximo metade da memória da máquina.
- Abrir o Docker Desktop, rodar `docker compose up -d` e esperar `healthy` nos dois serviços (2 a 3 minutos). Logo após iniciar, o Kibana ainda executa tarefas internas por alguns minutos; por isso, subir o ambiente com antecedência.
- Deixar abertos: `data/acessos.csv` em um editor e o Kibana na **Home**, com zoom do navegador em 125% para leitura no projetor.
- Deixar o vídeo de contingência pronto para reproduzir.

## 2. Roteiro cronometrado

| Tempo | Ação | Fala de apoio |
|---|---|---|
| 00:00 | Mostrar `data/acessos.csv` | "Cada linha é uma requisição: horário, rota, método, status e tempo de resposta. São 70 linhas de um dia." |
| 00:30 | **Home** → **Upload a file** → *Index name*: `acessos` → selecionar o CSV | "O Kibana lê o arquivo e infere os tipos: `endpoint` virou keyword, `status_code` número, `timestamp` data. Ele também criou `@timestamp`." |
| 01:15 | **Advanced options** → desligar **Create data view** → **Import** | "O Data View já veio com o dashboard. As etapas mostram o índice criado e os documentos enviados ao Elasticsearch." |
| 01:45 | Busca do topo → **Discover** → **Search entire time range** | "70 documentos, um por linha do CSV. Os dados são de 01/10, por isso ampliamos o intervalo de tempo." Abrir um documento e mostrar os campos. |
| 02:30 | Na barra de busca: `status_code >= 500` + Enter | "Seis erros 500, todos em `/pedidos`, entre 14h11 e 15h03. Encontramos o incidente." |
| 03:15 | Apagar a busca → clicar no campo `endpoint` → **Visualize** | "O Lens montou o gráfico sozinho: `/pedidos` é a rota mais acessada. Embaixo ficam outras sugestões de gráfico." |
| 03:45 | **Save** → *Title*: `Endpoints mais acessados` → **Existing** → *Acessos da aplicação (logs fictícios)* → **Save and go to dashboard** → **Save** → **Exit edit** | "A visualização entra no dashboard junto com as quatro que já existiam." |
| 04:15 | No dashboard, clicar no trecho vermelho da barra das 14h → **Apply** | "Um clique filtra todos os painéis: são 5 erros nessa hora, com tempo médio de 2.527 ms." (O Kibana exibe `2,527` porque usa o formato numérico em inglês.) |
| 05:00 | Encerrar e voltar aos slides | "CSV, índice, documentos e campos, Data View, Discover, Lens e Dashboard: o fluxo completo." |

Para desfazer o filtro do clique, remova o filtro `status_code: 500` no **x** e reabra o dashboard (ele volta ao intervalo salvo, 01/10/2026 das 07:00 às 19:00).

Se sobrar tempo: no Discover, `status_code : 401` mostra as 5 tentativas de login negadas, um exemplo de uso em segurança.

## 3. Diagnóstico rápido

No Windows PowerShell, use `curl.exe` em vez de `curl`.

| Comando | Resultado esperado |
|---|---|
| `docker compose ps` | `elasticsearch` e `kibana` com status `healthy` |
| `curl http://localhost:9200` | JSON com `"number" : "9.5.5"` |
| `curl "http://localhost:9200/_cat/indices/acessos?v"` | índice `acessos` com `docs.count` 70 (status `yellow` é normal com um nó) |
| `curl http://localhost:5601/api/status` | `{"status":{"overall":{"level":"available"}}}` |
| `docker compose logs --tail 50 kibana` | últimas linhas do log do Kibana |
| `docker compose logs --tail 50 elasticsearch` | últimas linhas do log do Elasticsearch |
| `docker stats --no-stream` | consumo de memória de cada container |

O log do Kibana registra avisos de recursos que a demonstração não usa (Fleet, Cloud Connect, telemetria) e, às vezes, erros genéricos `500 Server Error`. Nos testes, nenhum deles afetou a demonstração: o que importa é o status `healthy` e as telas funcionando.

## 4. Se algum container estiver parado

1. Docker Desktop fechado: abrir e esperar o motor iniciar (*Engine running*).
2. Rodar `docker compose up -d`: o comando só inicia o que estiver parado e não apaga dados.
3. Kibana sem responder: `docker compose restart kibana` e esperar de 2 a 4 minutos.
4. Container parado com `Exited (137)` ou tudo muito lento: falta de memória. Fechar programas e repetir o passo 2. No Windows, a memória da VM do Docker pode ser aumentada no arquivo `%UserProfile%\.wslconfig` (seção `[wsl2]`, linha `memory=6GB`, seguido de `wsl --shutdown`); no macOS, em Docker Desktop → *Settings → Resources*.
5. Erro de porta em uso (9200 ou 5601): outro Elasticsearch ou Kibana está rodando na máquina. Pare-o e repita o passo 2.
6. Log do Elasticsearch com `OutOfMemoryError` ou `circuit_breaking_exception`: aumentar a memória da JVM no `docker-compose.yml` para `ES_JAVA_OPTS=-Xms1g -Xmx1g` e rodar `docker compose up -d`.

## 5. Plano de recuperação

| Sintoma | Ação |
|---|---|
| "Kibana server is not ready yet" | Aguardar até 4 minutos; conferir `docker compose logs --tail 50 kibana` e a memória (seção 4, passo 4). |
| Upload: "Index name already exists" e **Import** desabilitado | Os dados já foram carregados (por exemplo, no ensaio). Seguir para o Discover, ou apagar o índice (seção 1, passo 7) e refazer. |
| Upload termina com "Error creating data view" (`DuplicateDataViewError`) | **Create data view** ficou ligado. Os dados foram carregados normalmente; seguir. |
| Discover sem resultados | Clicar em **Search entire time range** (os dados são de 01/10/2026). |
| Dashboard vazio | Conferir o índice (`_cat/indices/acessos` com 70 documentos) e se o intervalo de tempo cobre 01/10/2026. |
| Dashboard não aparece na lista | Reimportar `kibana/dashboard_acessos.ndjson`. |
| Ambiente irrecuperável | `docker compose down -v`, `docker compose up -d`, reimportar o dashboard e refazer o upload (≈ 4 minutos). Durante a apresentação, usar a contingência. |

**Regra prática:** se o problema não for resolvido em cerca de 1 minuto, passar para a contingência.

## 6. Contingência: gravação prévia

A avaliação aceita gravação apenas como contingência em caso de dificuldade técnica justificada. Por isso:

- **Quando gravar:** na véspera, durante o ensaio (seção 1, passo 6), seguindo exatamente a seção 2 (≈ 5 minutos).
- **Como gravar:** no Windows, Xbox Game Bar (**Win + Alt + R** inicia e para a gravação da janela do navegador) ou OBS Studio; no macOS, **Cmd + Shift + 5**. Usar resolução 1920×1080, zoom de 125% e notificações desligadas. De preferência sem áudio, para narrar ao vivo.
- **Onde guardar:** no computador da apresentação, para tocar sem internet, e uma cópia em pendrive. Testar a reprodução antes da aula.
- **Como usar:** explicar brevemente à turma a dificuldade técnica, reproduzir o vídeo e narrar os mesmos pontos da coluna "Fala de apoio".
- **Último recurso:** o slide de apoio ao final da apresentação mostra o dashboard esperado.
