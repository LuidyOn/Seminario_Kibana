# Kibana: conteúdo do seminário

Material de apoio, em nível introdutório, para a parte teórica do seminário. Os números entre colchetes remetem a [referencias.md](referencias.md). A demonstração usa **eventos reais do Windows** coletados no próprio computador da apresentação, processados pelo **Logstash** e analisados no **Kibana** (Elastic Stack 9.5.5). Os valores mostrados variam de um computador para outro.

## 1. Situação-problema

Imagine o suporte de um laboratório em que alguns aplicativos começam a falhar. Para investigar, a equipe precisa descobrir quando as falhas começaram, quantas vezes ocorreram e quais fontes aparecem nos registros. Esse cenário é hipotético. A captura do Visualizador de Eventos mostra o canal Aplicativo no computador da demonstração.

O Windows registra continuamente o que acontece com aplicativos e serviços: falhas, avisos, instalações, atualizações. Esses registros ficam no **Visualizador de Eventos**, separados em canais como Aplicativo (*Application*), Sistema e Segurança. No computador usado nos testes deste trabalho, o canal Aplicativo registrou cerca de 440 eventos em 24 horas (medido em 29/10/2026).

Olhando evento por evento, é difícil responder:

- Quantos erros e avisos aconteceram na semana?
- Quais aplicativos ou serviços mais registram eventos?
- Em que momentos os problemas se concentram?
- Chegou algum evento novo agora?

Para responder, é preciso **coletar** os eventos, **guardá-los** de forma pesquisável e **visualizá-los**. Na Elastic Stack, o Logstash cuida da ingestão, o Elasticsearch armazena e pesquisa, e o Kibana apresenta.

## 2. Dos registros ao painel

```text
Windows
Windows Event Log (Application) → coletor PowerShell → eventos.jsonl

Docker Compose
Logstash lê o arquivo → Elasticsearch (índice windows-events)
Kibana ── consulta ──► Elasticsearch
Kibana ◄─ resposta ─── Elasticsearch
```

O coletor roda diretamente no Windows porque lê o canal Aplicativo desse computador. Logstash, Elasticsearch e Kibana rodam em containers iniciados pelo `docker compose`. A demonstração usa a mesma versão nos três componentes, a 9.5.5 [1] [20] [23] [24] [25].

| | Logstash | Elasticsearch | Kibana |
|---|---|---|---|
| Papel | Lê e prepara os eventos com entradas, filtros e saídas [1] [9] | Armazena, pesquisa e agrega os documentos [1] [2] | Consulta e apresenta os resultados [1] |
| Na demo | Acompanha o JSONL do coletor | Guarda o índice `windows-events` | Data View, Discover, Lens e Dashboard |
| Acesso | Interno ao Docker | API REST (porta 9200) | Navegador (porta 5601) |

## 3. Coleta dos eventos do Windows

O coletor `scripts/coletar_eventos.ps1` usa o cmdlet `Get-WinEvent`, que lê os logs de eventos do Windows e devolve os eventos do mais recente para o mais antigo [15]. O canal Aplicativo pode ser lido sem privilégios de administrador.

- **Primeira execução:** amostra com os eventos dos últimos 7 dias, limitada a 2.000.
- **Depois:** a cada 15 segundos, lê só os eventos com `RecordId` maior que o último exportado (checkpoint em `runtime/state/checkpoint.json`). Como o `RecordId` é único e crescente no canal, horários empatados não causam problema.
- **Nível normalizado** a partir do valor numérico do evento [16] [17]: 1 Critical, 2 Error, 3 Warning, 4 Information, 5 Verbose. O nível 0 (*LogAlways*) aparece como "Informações" no Visualizador de Eventos e também vira Information.
- **Privacidade:** o coletor exporta horário (UTC), canal, provedor, ID do evento, `RecordId`, nível e um identificador aleatório da instalação. Mensagem, usuário, nome do computador e dados internos ficam de fora. Horário e provedor podem revelar contexto. A pasta `runtime/` fica fora do Git.
- **Sem duplicação:** cada evento recebe um ID estável (`Application-<RecordId>-<horário>`). Se o coletor ou o Logstash relerem eventos, o Elasticsearch apenas sobrescreve o mesmo documento.
- **Transparência:** se o log for limpo, ou se eventos forem descartados pelo log circular do Windows antes da coleta, o coletor registra um aviso em `runtime/state/coletor.log`.
- **Não é instantâneo:** um evento novo aparece no Kibana depois do intervalo de leitura (até 15 s) mais o tempo de leitura do Logstash.

**JSON Lines.** Cada linha de `runtime/logs/eventos.jsonl` contém um objeto JSON para um evento. A coleta verifica o Windows periodicamente. O Logstash acompanha o arquivo entre verificações.

## 4. Logstash

O Logstash processa cada evento em três estágios: **entradas** geram eventos, **filtros** os modificam e **saídas** os enviam a outro lugar [9]. *Codecs* decodificam ou codificam os dados dentro de uma entrada ou saída, sem precisar de um filtro separado [9].

O pipeline da demonstração (`logstash/pipeline/windows-events.conf`):

| Estágio | Plugin | O que faz |
|---|---|---|
| Entrada | `file` | Acompanha `eventos.jsonl` e lê cada linha nova; o *sincedb* guarda até onde o arquivo já foi lido [10] |
| Codec | `json` | Converte cada linha em evento. A Elastic orienta usar `json`, e não `json_lines`, com entradas orientadas a linhas como `file` [11] |
| Filtro | `mutate` | Remove campos técnicos acrescentados pelo Logstash |
| Saída | `elasticsearch` | Grava no índice `windows-events` usando o ID do próprio evento (`document_id`), o que sobrescreve em vez de duplicar [12] |

No Docker, o diretório de pipelines é montado em `/usr/share/logstash/pipeline/`, substituindo o pipeline de exemplo da imagem [13]. A memória da JVM foi limitada a 256 MB via `LS_JAVA_OPTS` [14] por causa do volume mínimo da demo; é bem abaixo da recomendação da Elastic para ingestão típica (4 a 8 GB) [14].

## 5. Elasticsearch

A indexação organiza os documentos do projeto para busca e análise. O Logstash envia cada evento ao índice `windows-events` e informa seu identificador estável. Em uma releitura, um documento com o mesmo ID é atualizado.

| Conceito | Definição | Na demonstração |
|---|---|---|
| **Índice** | Conjunto de documentos pesquisáveis [2] | `windows-events` |
| **Documento** | Um registro JSON formado por campos [2] | Um evento do Windows |
| **Campo** | Atributo do documento com tipo definido no mapeamento [2] | `@timestamp` (date), `log.level` (keyword), `winlog.record_id` (long) |

Um campo `keyword` permite filtrar e agrupar por valor exato, como nível ou provedor. Um campo `date` organiza o histograma no tempo. Um `long` representa números inteiros, como o RecordId. O template `logstash/windows-events-template.json` é instalado pelo Logstash [12].

## 6. O que é o Kibana

O Kibana é a interface web da Elastic Stack para explorar e visualizar os dados armazenados no Elasticsearch [1]. Uma pergunta como “Que erros ocorreram nesta semana?” vira uma consulta com um intervalo de tempo e um filtro por nível. O Elasticsearch busca ou agrega os dados. O Kibana mostra a resposta no navegador.

Os documentos e os objetos salvos do Kibana, como Data Views, visualizações e dashboards, ficam em índices do Elasticsearch [1] [8].

## 7. Ferramentas do Kibana

### Data View

O Data View é a "ponte" entre o Kibana e os índices: sem ele, os dados não aparecem no Discover nem no Lens [3]. Ele define o padrão de índice (`windows-events`) e o campo de tempo (`@timestamp`); sem campo de tempo, não há filtro de tempo global nos dashboards [3].

### Discover

O Discover é a principal ferramenta para explorar os dados do Elasticsearch no Kibana [4]: mostra os documentos e o histograma no tempo, aceita pesquisas em KQL, Lucene ou ES|QL e exibe estatísticas de cada campo [4]. Ele sempre trabalha dentro de um intervalo de tempo; se nada aparecer, o botão **Search entire time range** amplia o intervalo.

### KQL

A KQL (*Kibana Query Language*) filtra documentos [5]. No exemplo da apresentação, `log.level : "Error"` deixa visíveis apenas os erros. Para incluir avisos, use `log.level : "Warning" or log.level : "Error"`. Agregações, transformações e ordenação ficam a cargo de outras operações.

### Lens

O Lens é o editor de visualizações do Kibana para gráficos, tabelas, mapas e métricas [6]: arrasta-se um campo e ele sugere visualizações [6]. Atalho usado na demonstração: no Discover, clicar em um campo e escolher **Visualize** abre o Lens com um gráfico daquele campo.

### Dashboard

Um dashboard combina várias visualizações numa única visão interativa [7]. O filtro de tempo e a barra de pesquisa valem para todos os painéis, e clicar em um gráfico cria filtros aplicados ao painel inteiro. Dashboards, visualizações e Data Views são **objetos salvos**, exportados e importados como arquivos NDJSON [8]. O dashboard da demo (`kibana/dashboard_eventos.ndjson`) é importado automaticamente pelo script de início e se atualiza a cada 30 segundos.

## 8. Vantagens

- **Visualização sem programação:** crie gráficos pela interface do Kibana. A coleta e a ingestão usam scripts e configurações.
- **Integração nativa:** as buscas e agregações são executadas pelo Elasticsearch.
- **Ingestão flexível:** o Logstash combina entradas, filtros e saídas por configuração [9].
- **Interatividade:** filtro de tempo global e filtros por clique em todos os painéis.
- **Gratuito para o essencial:** a demonstração roda na licença gratuita *Basic*; a Elastic oferece o nível *Free and open* [26].
- **Portabilidade:** pipeline, mapeamento e dashboard ficam no repositório; cada computador coleta os próprios eventos.
- **Expansão:** novas fontes podem entrar por outros plugins do Logstash. Em produção, agentes como o Elastic Agent podem enviar registros de várias máquinas ao Elasticsearch [1].

## 9. Limitações e aplicações

### Limitações da demonstração

- **Memória:** são três serviços. A demonstração usa heaps de 512 MB no Elasticsearch e 256 MB no Logstash. O consumo total varia com a inicialização e as consultas, e pode ser conferido com `docker stats --no-stream`.
- **Coleta periódica:** os eventos chegam em ciclos de 15 s, não no instante em que acontecem.
- **Escopo restrito por escolha:** só o canal Aplicativo e só metadados; sem mensagens, por privacidade.
- **Segurança exige configuração:** desativar a segurança "não é recomendado" [22]; aqui ela foi desligada apenas para simplificar a demonstração local.
- **Solução didática para Windows:** um computador, um nó, sem alta disponibilidade; não é uma arquitetura de produção.
- **Recursos pagos:** parte dos recursos avançados exige assinatura; por exemplo, regras de alerta baseadas em detecção de anomalias só existem nos níveis Platinum e Enterprise [26].
- **Configuração e manutenção:** o coletor, o pipeline e o ambiente Docker precisam de acompanhamento. Uma instalação de produção também precisa de autenticação, TLS e controles adequados ao ambiente [22].

### Aplicações

- **Suporte e TI:** encontrar falhas de aplicativos e serviços recorrentes nos computadores de uma equipe.
- **Monitoramento de logs:** a solução de observabilidade da Elastic é voltada a logs em grande escala [27].
- **Segurança:** a solução Elastic Security (SIEM) usa os recursos de visualização do Kibana [28].
- **Vários computadores:** em produção, agentes como o Elastic Agent enviam logs de muitas máquinas para o mesmo Elasticsearch [1].

## 10. Demonstração prática

O penúltimo slide leva a uma única sequência ao vivo de cerca de cinco minutos. A execução começa no Visualizador de Eventos e termina nos filtros do dashboard. Consulte o [roteiro da demonstração](roteiro_demonstracao.md).

**Fonte:** canal Aplicativo do Windows do próprio computador da apresentação, apenas metadados (seção 3).

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

## 11. Conclusão e perguntas

O Windows fornece os eventos reais. O Logstash prepara esses registros e o Elasticsearch os torna pesquisáveis. O Kibana permite explorar as respostas com filtros e gráficos. A [bibliografia do seminário](referencias.md) reúne as fontes para consulta.
