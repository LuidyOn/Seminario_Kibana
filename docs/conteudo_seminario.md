# Kibana: conteúdo do seminário

Material de apoio, em nível introdutório, para a parte teórica do seminário. Os números entre colchetes remetem a [referencias.md](referencias.md). A demonstração usa **eventos reais do Windows** coletados no próprio computador da apresentação, processados pelo **Logstash** e analisados no **Kibana** (Elastic Stack 9.5.5). Os valores mostrados variam de um computador para outro.

## 1. O problema que o Kibana resolve

O Windows registra continuamente o que acontece com aplicativos e serviços: falhas, avisos, instalações, atualizações. Esses registros ficam no **Visualizador de Eventos**, separados em canais como Aplicativo (*Application*), Sistema e Segurança. No computador usado nos testes deste trabalho, o canal Aplicativo registrou cerca de 440 eventos em 24 horas (medido em 29/10/2026).

Olhando evento por evento, é difícil responder:

- Quantos erros e avisos aconteceram na semana?
- Quais aplicativos ou serviços mais registram eventos?
- Em que momentos os problemas se concentram?
- Chegou algum evento novo agora?

Para responder, é preciso **coletar** os eventos, **guardá-los** de forma pesquisável e **visualizá-los**. Na Elastic Stack, o Logstash cuida da ingestão, o Elasticsearch armazena e pesquisa, e o Kibana apresenta.

## 2. O que é o Kibana

O Kibana é a **interface de usuário da Elastic Stack**: uma aplicação web para visualizar e analisar os dados armazenados no Elasticsearch [1]. Pelo navegador, e sem programar, é possível:

- pesquisar e filtrar documentos (**Discover**);
- montar gráficos arrastando campos (**Lens**);
- reunir visualizações em painéis interativos (**Dashboards**).

## 3. Relação entre Kibana, Elasticsearch e Logstash

| | Logstash | Elasticsearch | Kibana |
|---|---|---|---|
| Papel | Coleta e prepara os dados: entradas, filtros e saídas [1] [9] | Motor de busca e análise e repositório dos dados [1] | Interface para explorar e visualizar os dados [1] |
| Na demo | Lê o arquivo gerado pelo coletor e envia os eventos | Guarda o índice `windows-events` | Data View, Discover, Lens e Dashboard |
| Acesso | Interno ao Docker | API REST (porta 9200) | Navegador (porta 5601) |

Pontos importantes:

- O Kibana **não guarda os dados analisados**: cada tabela ou gráfico é uma consulta ao Elasticsearch. Até os objetos do próprio Kibana (Data Views, visualizações, dashboards) ficam em índices do Elasticsearch.
- A Elastic exige **a mesma versão** em todos os componentes da stack [1] [20]. Na demonstração, os três estão na 9.5.5 [23] [24] [25].

## 4. Conceitos fundamentais

| Conceito | Definição simples | Na nossa demonstração |
|---|---|---|
| **Logstash** | Organiza a ingestão de dados em entradas, filtros e saídas [1] [9] | Container `logstash` |
| **Pipeline** | Caminho de cada evento: entrada → filtro → saída [9] | `logstash/pipeline/windows-events.conf` |
| **JSON Lines** | Arquivo de texto com um objeto JSON por linha | `runtime/logs/eventos.jsonl` |
| **Elasticsearch** | Motor de busca e análise que armazena dados como documentos JSON [1] [2] | Container `elasticsearch` |
| **Índice** | Unidade fundamental de armazenamento do Elasticsearch [2] | `windows-events` |
| **Documento** | Registro em JSON formado por campos (pares chave-valor) [2] | Um evento do Windows |
| **Campo** | Cada atributo do documento, com tipo definido no *mapping* do índice [2] | `log.level` (keyword), `@timestamp` (date), `winlog.record_id` (long) |
| **Data View** | Diz ao Kibana quais índices consultar e qual campo representa o tempo [3] | `windows-events`, campo de tempo `@timestamp` |
| **Discover** | Ferramenta para explorar, pesquisar e filtrar documentos [4] | Ver os eventos e filtrar por nível |
| **Lens** | Editor de visualizações: arrasta-se o campo e o Kibana sugere o gráfico [6] | Gráfico dos IDs de evento mais frequentes |
| **Dashboard** | Painel que combina várias visualizações numa única tela interativa [7] | "Eventos do Windows" |

Também usamos a **KQL** (*Kibana Query Language*), linguagem textual de filtro [5]. Exemplos: `log.level : "Error"` e `log.level : "Warning" or log.level : "Error"`. A KQL apenas filtra; não agrega, não transforma e não ordena [5].

**Por que o tipo do campo importa:** um campo `keyword` serve para agrupar e filtrar por valor exato (nível, provedor), um campo de data permite o histograma no tempo e um campo numérico permite ordenar e calcular. Os tipos do índice `windows-events` são definidos por um *template* instalado pelo próprio Logstash [12].

## 5. Logstash

O Logstash processa cada evento em três estágios: **entradas** geram eventos, **filtros** os modificam e **saídas** os enviam a outro lugar [9]. *Codecs* decodificam ou codificam os dados dentro de uma entrada ou saída, sem precisar de um filtro separado [9].

O pipeline da demonstração (`logstash/pipeline/windows-events.conf`):

| Estágio | Plugin | O que faz |
|---|---|---|
| Entrada | `file` | Acompanha `eventos.jsonl` e lê cada linha nova; o *sincedb* guarda até onde o arquivo já foi lido [10] |
| Codec | `json` | Converte cada linha em evento. A Elastic orienta usar `json`, e não `json_lines`, com entradas orientadas a linhas como `file` [11] |
| Filtro | `mutate` | Remove campos técnicos acrescentados pelo Logstash |
| Saída | `elasticsearch` | Grava no índice `windows-events` usando o ID do próprio evento (`document_id`), o que sobrescreve em vez de duplicar [12] |

No Docker, o diretório de pipelines é montado em `/usr/share/logstash/pipeline/`, substituindo o pipeline de exemplo da imagem [13]. A memória da JVM foi limitada a 256 MB via `LS_JAVA_OPTS` [14] por causa do volume mínimo da demo; é bem abaixo da recomendação da Elastic para ingestão típica (4 a 8 GB) [14].

## 6. Coleta dos eventos do Windows

O coletor `scripts/coletar_eventos.ps1` usa o cmdlet `Get-WinEvent`, que lê os logs de eventos do Windows e devolve os eventos do mais recente para o mais antigo [15]. O canal Aplicativo pode ser lido sem privilégios de administrador.

- **Primeira execução:** amostra com os eventos dos últimos 7 dias, limitada a 2.000.
- **Depois:** a cada 15 segundos, lê só os eventos com `RecordId` maior que o último exportado (checkpoint em `runtime/state/checkpoint.json`). Como o `RecordId` é único e crescente no canal, horários empatados não causam problema.
- **Nível normalizado** a partir do valor numérico do evento [16] [17]: 1 Critical, 2 Error, 3 Warning, 4 Information, 5 Verbose. O nível 0 (*LogAlways*) aparece como "Informações" no Visualizador de Eventos e também vira Information.
- **Privacidade:** o coletor exporta horário (UTC), canal, provedor, ID do evento, `RecordId`, nível e um identificador aleatório da instalação. Mensagem, usuário, nome do computador e dados internos ficam de fora. Horário e provedor podem revelar contexto. A pasta `runtime/` fica fora do Git.
- **Sem duplicação:** cada evento recebe um ID estável (`Application-<RecordId>-<horário>`). Se o coletor ou o Logstash relerem eventos, o Elasticsearch apenas sobrescreve o mesmo documento.
- **Transparência:** se o log for limpo, ou se eventos forem descartados pelo log circular do Windows antes da coleta, o coletor registra um aviso em `runtime/state/coletor.log`.
- **Não é instantâneo:** um evento novo aparece no Kibana depois do intervalo de leitura (até 15 s) mais o tempo de leitura do Logstash.

## 7. Arquitetura básica

```text
Windows Event Log (canal Application)
      │  Get-WinEvent a cada 15 s
      ▼
Coletor PowerShell ──► runtime/logs/eventos.jsonl (um JSON por linha)
                              │  leitura contínua do arquivo
                              ▼
               Logstash ──► Elasticsearch (índice windows-events) ──► Kibana ──► navegador
               └────────────── Docker Compose (local) ──────────────┘
```

O coletor roda no Windows (fora do Docker), porque precisa ler o log de eventos do próprio computador. Logstash, Elasticsearch e Kibana rodam em containers iniciados pelo `docker compose`. Em produção, a Elastic oferece o Elastic Agent como forma unificada de coletar logs e métricas de um computador [1]; aqui o coletor simples mantém o foco no Logstash e no Kibana.

## 8. Data Views

O Data View é a "ponte" entre o Kibana e os índices: sem ele, os dados não aparecem no Discover nem no Lens [3]. Ele define o padrão de índice (`windows-events`) e o campo de tempo (`@timestamp`); sem campo de tempo, não há filtro de tempo global nos dashboards [3].

## 9. Discover

O Discover é a principal ferramenta para explorar os dados do Elasticsearch no Kibana [4]: mostra os documentos e o histograma no tempo, aceita pesquisas em KQL, Lucene ou ES|QL e exibe estatísticas de cada campo [4]. Ele sempre trabalha dentro de um intervalo de tempo; se nada aparecer, o botão **Search entire time range** amplia o intervalo.

## 10. Lens

O Lens é o editor de visualizações do Kibana para gráficos, tabelas, mapas e métricas [6]: arrasta-se um campo e ele sugere visualizações [6]. Atalho usado na demonstração: no Discover, clicar em um campo e escolher **Visualize** abre o Lens com um gráfico daquele campo.

## 11. Dashboard

Um dashboard combina várias visualizações numa única visão interativa [7]. O filtro de tempo e a barra de pesquisa valem para todos os painéis, e clicar em um gráfico cria filtros aplicados ao painel inteiro. Dashboards, visualizações e Data Views são **objetos salvos**, exportados e importados como arquivos NDJSON [8]. O dashboard da demo (`kibana/dashboard_eventos.ndjson`) é importado automaticamente pelo script de início e se atualiza a cada 30 segundos.

## 12. Vantagens

- **Visualização sem programação:** crie gráficos pela interface do Kibana. A coleta e a ingestão usam scripts e configurações.
- **Integração nativa:** as buscas e agregações são executadas pelo Elasticsearch.
- **Ingestão flexível:** o Logstash combina entradas, filtros e saídas por configuração [9].
- **Interatividade:** filtro de tempo global e filtros por clique em todos os painéis.
- **Gratuito para o essencial:** a demonstração roda na licença gratuita *Basic*; a Elastic oferece o nível *Free and open* [26].
- **Portabilidade:** pipeline, mapeamento e dashboard ficam no repositório; cada computador coleta os próprios eventos.

## 13. Limitações

- **Memória:** são três serviços. A demonstração usa heaps de 512 MB no Elasticsearch e 256 MB no Logstash. O consumo total varia com a inicialização e as consultas, e pode ser conferido com `docker stats --no-stream`.
- **Coleta periódica:** os eventos chegam em ciclos de 15 s, não no instante em que acontecem.
- **Escopo restrito por escolha:** só o canal Aplicativo e só metadados; sem mensagens, por privacidade.
- **Segurança exige configuração:** desativar a segurança "não é recomendado" [22]; aqui ela foi desligada apenas para simplificar a demonstração local.
- **Solução didática para Windows:** um computador, um nó, sem alta disponibilidade; não é uma arquitetura de produção.
- **Recursos pagos:** parte dos recursos avançados exige assinatura; por exemplo, regras de alerta baseadas em detecção de anomalias só existem nos níveis Platinum e Enterprise [26].

## 14. Exemplos de uso

- **Suporte e TI:** encontrar falhas de aplicativos e serviços recorrentes nos computadores de uma equipe.
- **Monitoramento de logs:** a solução de observabilidade da Elastic é voltada a logs em grande escala [27].
- **Segurança:** a solução Elastic Security (SIEM) usa os recursos de visualização do Kibana [28].
- **Vários computadores:** em produção, agentes como o Elastic Agent enviam logs de muitas máquinas para o mesmo Elasticsearch [1].

## 15. A nossa demonstração

**Fonte:** canal Aplicativo do Windows do próprio computador da apresentação, apenas metadados (seção 6).

| Campo | Exemplo | Significado |
|---|---|---|
| `@timestamp` | `2026-10-29T14:05:12.000Z` | Quando o evento ocorreu (UTC; o Kibana exibe no fuso do navegador) |
| `log.level` | `Error` | Nível normalizado: Critical, Error, Warning, Information ou Verbose |
| `event.provider` | `Application Error` | Provedor (fonte) do evento |
| `event.code` | `1000` | ID do evento |
| `winlog.record_id` | `50123` | Número sequencial do evento no canal |

Os exemplos acima ilustram o formato; os dados reais variam conforme o computador.

**Como cada passo se liga aos conceitos:**

| Passo | Conceito |
|---|---|
| Visualizador de Eventos | Fonte de dados |
| Coletor e `eventos.jsonl` | Coleta automática e incremental, JSON Lines |
| Logstash | Pipeline: entrada `file` → filtro → saída `elasticsearch` |
| Elasticsearch | Índice `windows-events`, documentos e tipos dos campos |
| Discover e filtro KQL | Explorar documentos dentro de um intervalo de tempo, pelo Data View |
| Lens | Transformar um campo em gráfico |
| Dashboard | Reunir as visualizações; um clique filtra todos os painéis |
