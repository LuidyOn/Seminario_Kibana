# Kibana na prática: eventos reais do Windows com Logstash e Elasticsearch

Demonstração didática do **Kibana** para o seminário técnico da disciplina **Projeto de Desenvolvimento de Dashboard Analítico** (Avaliação de Produto 2): apresentação de 7 a 20 minutos com slides e demonstração prática da ferramenta.

> **Ambiente local didático para demonstração e desenvolvimento, não destinado à produção.**

## Objetivo

Mostrar, com **eventos reais do Windows do próprio computador**, como os dados são coletados automaticamente, processados pelo **Logstash**, armazenados no **Elasticsearch** e analisados no **Kibana**: Discover, filtros KQL, Lens e Dashboard.

## Arquitetura

```text
Windows Event Log (canal Application)
      │  Get-WinEvent, a cada 15 s (scripts/coletar_eventos.ps1, roda no Windows)
      ▼
runtime/logs/eventos.jsonl   ← um JSON por linha; só neste computador, fora do Git
      │  leitura contínua do arquivo
      ▼
Logstash 9.5.5 ── entrada file + codec json → filtro → saída elasticsearch
      ▼
Elasticsearch 9.5.5 ── índice windows-events                            porta 9200
      ▼
Kibana 9.5.5 ── Data View → Discover · Lens · Dashboard "Eventos do Windows"   porta 5601
```

Logstash, Elasticsearch e Kibana rodam em containers definidos em [docker-compose.yml](docker-compose.yml), na mesma versão (exigência da Elastic). Elasticsearch e Kibana aceitam conexões apenas da própria máquina (`127.0.0.1`); o Logstash não expõe portas.

| Caminho | Finalidade |
|---|---|
| `docker-compose.yml` | Sobe Elasticsearch, Logstash e Kibana (nó único, ambiente local) |
| `scripts/iniciar_demo.ps1` | Um comando para subir tudo: containers, coletor e dashboard |
| `scripts/parar_demo.ps1` | Para o coletor e os containers, preservando os dados |
| `scripts/coletar_eventos.ps1` | Coletor: lê o canal Application e grava `runtime/logs/eventos.jsonl` |
| `logstash/pipeline/windows-events.conf` | Pipeline do Logstash (entrada, filtro e saída) |
| `logstash/windows-events-template.json` | Tipos dos campos do índice `windows-events` |
| `kibana/dashboard_eventos.ndjson` | Objetos do Kibana: Data View, 4 visualizações e o dashboard |
| `docs/` | Conteúdo do seminário, roteiros e referências |
| `slides/` | Apresentação (`.pptx`) e o script que a gera |
| `runtime/` | Criada na primeira execução: eventos coletados e estado da coleta (**ignorada pelo Git**) |

## O que é coletado

- **Coletado:** horário do evento (UTC), canal (`Application`), provedor (fonte), ID do evento, `RecordId`, nível normalizado (`Critical`, `Error`, `Warning`, `Information` ou `Verbose`) e um identificador aleatório desta instalação.
- **Não coletado:** a mensagem do evento, usuário, nome do computador, processos e os dados internos do evento. O canal de Segurança não é lido.
- Os eventos e o estado da coleta ficam em `runtime/`, que o Git ignora. Cada computador coleta os próprios eventos.

## Pré-requisitos

- Windows 10 ou 11 com Windows PowerShell 5.1 (já incluso no sistema);
- Docker Desktop com Docker Compose v2;
- cerca de 3 GB de RAM livres para os containers. No Windows, a VM do Docker (WSL 2) usa por padrão no máximo metade da RAM da máquina; com 8 GB, feche outros programas antes de subir o ambiente;
- espaço em disco para as imagens (só as do Elasticsearch e do Kibana somam cerca de 5 GB) e internet na primeira execução, para baixá-las;
- navegador atualizado (Chrome, Edge ou Firefox).

## Como executar

Na pasta do projeto, num terminal PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\iniciar_demo.ps1
```

O `-ExecutionPolicy Bypass` vale só para esse comando e não altera a configuração do Windows. O script:

1. confere o Docker (e tenta iniciar o Docker Desktop, se estiver fechado) e avisa se houver pouca RAM livre;
2. cria a pasta `runtime\`;
3. sobe os containers e espera ficarem prontos (`docker compose up -d --wait`);
4. inicia o coletor em segundo plano, sem nunca abrir um segundo coletor;
5. importa o dashboard no Kibana, se ainda não existir;
6. confere se os eventos estão chegando ao índice `windows-events`.

Depois, abra <http://localhost:5601>. Na primeira visita, clique em **Explore on my own**; em seguida, **Dashboards** → **Eventos do Windows**.

O script pode ser executado de novo a qualquer momento: não duplica o coletor nem apaga dados. Com `-RestaurarDashboard`, o dashboard volta à versão original do repositório.

## Verificar

```powershell
docker compose ps                                      # elasticsearch e kibana "healthy"; logstash em execução
curl.exe http://localhost:9200/windows-events/_count   # quantidade de eventos no índice
Get-Content runtime\state\coletor.log -Tail 10         # atividade do coletor
```

## Parar

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\parar_demo.ps1
```

Para o coletor (por sinal, com checkpoint salvo) e os containers (`docker compose stop`). Nada é apagado: o índice, o dashboard e a pasta `runtime\` continuam disponíveis para a próxima execução. Com `-SomenteColetor`, os containers continuam no ar.

## Como a coleta funciona

- **Primeira execução:** importa os eventos dos últimos 7 dias, até 2.000.
- **Depois:** a cada 15 s, lê só os eventos com `RecordId` maior que o último exportado. O checkpoint fica em `runtime\state\checkpoint.json`. Novos eventos aparecem no Kibana após esse intervalo mais o tempo de leitura do Logstash; não é instantâneo.
- **Instância única:** um segundo coletor da mesma cópia do projeto se recusa a iniciar.
- **Sem duplicação no índice:** cada evento recebe um ID estável (`Application-<RecordId>-<horário>`), usado pelo Logstash como `document_id`. Se o arquivo for relido (por exemplo, se o Logstash perder a posição de leitura após reiniciar), os documentos são sobrescritos, não duplicados. Após uma falha, o arquivo pode conter linhas repetidas; o índice, não.
- **Avisos:** se o log do Windows for limpo, ou se eventos forem descartados pelo log circular antes da coleta, o coletor registra isso em `runtime\state\coletor.log`.
- O coletor só funciona enquanto o projeto está ativo; não há serviço nem tarefa agendada.

## Levar para outro computador

1. Clonar o repositório (nenhum evento real vai junto: `runtime/` não é versionada).
2. Abrir o Docker Desktop e executar `iniciar_demo.ps1`.
3. O coletor cria `runtime\` e coleta os eventos **daquele** computador; o dashboard é importado automaticamente.

## Validação

- **Testado no computador de desenvolvimento (29/10/2026):** o coletor leu 1.891 eventos reais dos últimos 7 dias e gerou JSON Lines válido, só com os campos permitidos; uma amostra conferiu com o `Get-WinEvent`; a coleta incremental, a instância única, a parada por sinal, a retomada pelo checkpoint e os avisos de log limpo e de lacuna funcionaram; uma cópia em outra pasta criou o próprio `runtime/`.
- **Ainda não executado de ponta a ponta:** Logstash → Elasticsearch → Kibana com esta configuração, por falta de memória livre naquele computador. Antes do seminário, siga a seção 1 de [docs/roteiro_demonstracao.md](docs/roteiro_demonstracao.md) no computador da apresentação e registre o resultado aqui.
- **Arquivos da versão anterior (dados fictícios):** `data/acessos.csv`, `kibana/dashboard_acessos.ndjson` e `slides/dashboard_kibana.png` não são usados pelo fluxo atual; ficam no repositório até a validação acima e depois serão removidos.

## Limitações do ambiente didático

- **Segurança desabilitada** (`xpack.security.enabled=false`): sem login e sem TLS, para simplificar a demonstração. É uma simplificação didática, nunca uma recomendação de produção; o próprio Kibana exibe o aviso *Your data is not secure*.
- **Nó único e memória reduzida:** Elasticsearch com 512 MB de heap e Logstash com 256 MB, abaixo da recomendação da Elastic para ingestão típica (4 a 8 GB). Adequado ao volume pequeno da demo, não a produção.
- **Coleta periódica e restrita:** verificação a cada 15 s, só o canal Application e só metadados.
- **Pasta compartilhada com o Docker:** a documentação do Logstash alerta que o controle de leitura (*sincedb*) pode não se manter em sistemas de arquivos remotos; por isso o ID estável evita duplicação se o arquivo for relido.
- **Somente Windows:** o coletor usa `Get-WinEvent`.

## Documentação

- [docs/conteudo_seminario.md](docs/conteudo_seminario.md): conteúdo teórico do seminário
- [docs/roteiro_apresentacao.md](docs/roteiro_apresentacao.md): roteiro da fala (≈ 16 min)
- [docs/roteiro_demonstracao.md](docs/roteiro_demonstracao.md): validação inicial, demonstração, diagnóstico e contingência
- [docs/referencias.md](docs/referencias.md): fontes consultadas

Os slides (`slides/seminario_kibana.pptx`) são gerados por `slides/gerar_slides.py`. Para regenerar: `pip install python-pptx` e `python slides/gerar_slides.py`.
