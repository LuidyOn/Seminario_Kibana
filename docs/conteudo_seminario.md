# Kibana: conteúdo do seminário

Material de apoio, em nível introdutório, para a parte teórica do seminário. Os números entre colchetes remetem a [referencias.md](referencias.md). O que aparece como "no nosso ambiente" foi observado na demonstração deste repositório (Elasticsearch e Kibana 9.5.5).

## 1. O problema que o Kibana resolve

Toda aplicação gera **logs**: a cada requisição, um registro com horário, rota acessada, resultado e tempo de resposta. Em pouco tempo são milhares de linhas, e lê-las uma a uma, ou mesmo em uma planilha, não responde bem a perguntas como:

- Quantas requisições falharam? Em qual rota?
- A aplicação ficou lenta? A partir de quando?
- Houve muitas tentativas de login negadas?

Para responder, é preciso **guardar** os dados de forma pesquisável e **visualizá-los** de modo que padrões e anomalias apareçam rápido. O Elasticsearch cuida da primeira parte; o Kibana, da segunda.

## 2. O que é o Kibana

O Kibana é a **interface de usuário da Elastic Stack**: uma aplicação web para visualizar e analisar os dados armazenados no Elasticsearch [1]. Pelo navegador, e sem programar, é possível:

- pesquisar e filtrar documentos (**Discover**);
- montar gráficos arrastando campos (**Lens**);
- reunir visualizações em painéis interativos (**Dashboards**).

## 3. Relação entre Kibana e Elasticsearch

| | Elasticsearch | Kibana |
|---|---|---|
| Papel | Motor distribuído de busca e análise e repositório dos dados [1] | Interface para explorar e visualizar esses dados [1] |
| Acesso | API REST (porta 9200) | Navegador (porta 5601) |
| O que guarda | Os documentos (no nosso caso, o índice `acessos`) | Nenhum dado analisado. Até os objetos do próprio Kibana (Data Views, visualizações, dashboards) ficam em índices do Elasticsearch (`.kibana_*`, no nosso ambiente) |

Pontos importantes:

- O Kibana **depende** do Elasticsearch: cada tabela ou gráfico é uma consulta enviada a ele.
- A Elastic exige **a mesma versão** em todos os componentes da stack [1] [12]. Na demonstração, os dois estão na versão 9.5.5, a mais recente nas notas de versão oficiais em 07/10/2026 [15] [16].

## 4. Conceitos fundamentais

| Conceito | Definição simples | Na nossa demonstração |
|---|---|---|
| **Elasticsearch** | Motor de busca e análise que armazena dados como documentos JSON [1] [2] | Container `elasticsearch` |
| **Índice** | Unidade fundamental de armazenamento do Elasticsearch [2] | `acessos` |
| **Documento** | Registro em JSON formado por campos, isto é, pares chave-valor [2] | Uma linha do CSV vira um documento (uma requisição) |
| **Campo** | Cada atributo do documento; o tipo de cada campo é definido no *mapping* do índice [2] | `status_code` (número), `endpoint` (keyword), `@timestamp` (data) |
| **Data View** | Diz ao Kibana quais índices consultar e qual campo representa o tempo [3] | `acessos`, com campo de tempo `@timestamp` |
| **Discover** | Ferramenta para explorar, pesquisar e filtrar documentos [4] | Ver as 70 requisições e isolar os erros |
| **Lens** | Editor de visualizações: arrasta-se o campo e o Kibana sugere o gráfico [6] | Gráfico "Endpoints mais acessados" |
| **Dashboard** | Painel que combina várias visualizações em uma única tela interativa [7] | "Acessos da aplicação (logs fictícios)" |

Também usamos a **KQL** (*Kibana Query Language*), linguagem textual de filtro [5]. Exemplos: `status_code >= 500`, `endpoint : "/login" and status_code : 401`. A KQL apenas filtra; não agrega, não transforma e não ordena [5].

**Por que o tipo do campo importa:** só um campo numérico permite calcular média, só um campo de data permite um histograma no tempo e um campo `keyword` serve para agrupar e filtrar por valor exato. No upload do nosso CSV, o Kibana inferiu: `endpoint` e `method` como `keyword`, `status_code` e `response_time_ms` como `long` e `timestamp` como `date`. Ele também criou o campo `@timestamp` (padrão do ecossistema Elastic), já convertido para UTC a partir do fuso `-03:00` do arquivo.

## 5. Arquitetura básica

```text
Fonte de dados  ──►  Elasticsearch  ──►  Kibana  ──►  Navegador
(CSV de logs)        (índice acessos)    (Data View,     (usuário)
                                          Discover, Lens,
                                          Dashboard)
```

1. **Ingestão:** os dados precisam chegar ao Elasticsearch. Em produção isso costuma ser feito por Elastic Agent ou Logstash [1], ou diretamente pelas APIs. Na demonstração, usamos o recurso **Upload a file** do Kibana: ele analisa o arquivo, sugere os tipos dos campos, cria o índice e envia os documentos [9].
2. **Armazenamento e busca:** o Elasticsearch indexa os documentos e responde às consultas.
3. **Visualização:** o Kibana transforma cliques e filtros em consultas ao Elasticsearch e desenha o resultado.

Na demonstração, Elasticsearch e Kibana rodam em containers Docker, com um único nó, iniciados por `docker compose up -d`. É um ambiente de desenvolvimento, não de produção [10] [13].

## 6. Data Views

O Data View é a "ponte" entre o Kibana e os índices: sem ele, os dados não aparecem no Discover nem no Lens [3]. Ele define:

- o **padrão de índice** (um nome como `acessos` ou um curinga como `logs-*`);
- o **campo de tempo**. Sem um campo de tempo padrão, não é possível usar o filtro de tempo global nos dashboards [3].

Na demonstração, o Data View `acessos` vem no arquivo exportado `kibana/dashboard_acessos.ndjson`, com `@timestamp` como campo de tempo.

## 7. Discover

O Discover é a principal ferramenta para explorar os dados do Elasticsearch no Kibana [4]. Nele é possível:

- ver os documentos e o histograma de quantidade ao longo do tempo;
- pesquisar com KQL, Lucene ou ES|QL e aplicar filtros [4];
- ver estatísticas de cada campo e abrir um documento para ver todos os seus campos [4].

O Discover sempre trabalha dentro de um **intervalo de tempo**. Como nossos dados são de 01/10/2026, o intervalo padrão ("Last 15 minutes") não mostra nada; o botão **Search entire time range** ajusta o intervalo para todo o período dos dados.

## 8. Lens

O Lens é o editor de visualizações do Kibana para gráficos, tabelas, mapas e métricas [6]. Arrasta-se um campo para a área de trabalho e ele **sugere** visualizações [6]. Tipos disponíveis incluem barras, linhas, áreas, pizza, treemap, métrica, gauge, tabela e mapa de calor [6].

Atalho usado na demonstração: no Discover, clicar em um campo e escolher **Visualize** abre o Lens com um gráfico pronto daquele campo.

## 9. Dashboard

Um dashboard combina várias visualizações, métricas e controles em uma única visão interativa [7]:

- o **filtro de tempo** e a barra de pesquisa valem para todos os painéis;
- **clicar em um gráfico** cria filtros que se aplicam ao painel inteiro (na demonstração, clicar na barra vermelha das 14h filtra todos os painéis para os erros 500 daquele horário);
- dashboards podem ser compartilhados [7] e, como outros **objetos salvos**, exportados e importados em arquivos NDJSON [8]. É assim que o dashboard da demonstração é distribuído neste repositório.

## 10. Vantagens

- **Exploração sem código:** pesquisar, filtrar e criar gráficos pela interface.
- **Integração nativa com o Elasticsearch:** as buscas e agregações são executadas pelo motor que armazena os dados.
- **Interatividade:** filtro de tempo global e filtros por clique em todos os painéis.
- **Rapidez para prototipar:** o Lens sugere a visualização a partir do campo escolhido.
- **Gratuito para o essencial:** a demonstração inteira roda na licença gratuita *Basic* (confirmado no nosso ambiente); a Elastic oferece o nível *Free and open* [17].
- **Portabilidade:** dashboards e visualizações podem ser exportados e importados como arquivo [8].

## 11. Limitações

- **Depende do Elasticsearch:** o Kibana visualiza o que está no Elasticsearch; os dados precisam ser ingeridos antes.
- **Consumo de recursos:** mesmo nesta demo mínima, o Kibana sozinho usou cerca de 1,5 GB de memória no nosso ambiente; somado ao Elasticsearch, é preciso ter cerca de 3 GB livres.
- **Curva de aprendizado:** mapeamento de campos, linguagens de consulta (KQL, Lucene, ES|QL) e uma interface com muitos menus.
- **Segurança exige configuração:** a segurança vem ativada por padrão no Elasticsearch, e desativá-la "não é recomendado" [14]. Aqui ela foi desligada apenas para simplificar a demonstração local.
- **Recursos pagos:** parte dos recursos avançados exige assinatura; por exemplo, regras de alerta baseadas em detecção de anomalias só existem nos níveis Platinum e Enterprise [17].
- **Upload a file não é ingestão de produção:** o recurso serve para exploração inicial, não para um processo repetitivo de produção [9].

## 12. Exemplos de uso

- **Monitoramento de logs de aplicações** (o caso da demonstração): erros, lentidão e rotas mais usadas. A Elastic oferece uma solução de observabilidade voltada a logs [18].
- **Segurança:** investigar tentativas de login negadas (status 401) e eventos suspeitos. A solução Elastic Security (SIEM) usa os recursos de visualização do Kibana [19].
- **Infraestrutura:** acompanhar métricas de servidores e serviços.
- **Indicadores de negócio:** por exemplo, pedidos por hora ou por canal, desde que os dados estejam no Elasticsearch.

## 13. A nossa demonstração

**Cenário:** logs fictícios de uma loja virtual em 01/10/2026, das 08h às 18h.

| Campo | Exemplo | Significado |
|---|---|---|
| `timestamp` | `2026-10-01T14:11:00-03:00` | Data e hora da requisição (horário de Brasília) |
| `endpoint` | `/pedidos` | Rota acessada |
| `method` | `POST` | Método HTTP |
| `status_code` | `500` | Resultado (200 ok, 401 não autorizado, 404 não encontrado, 500 erro interno) |
| `response_time_ms` | `2350` | Tempo de resposta em milissegundos |

**O que os dados revelam:**

- 70 requisições: 54 com sucesso (200), 5 logins negados (401), 5 acessos a uma página inexistente (404) e 6 erros internos (500);
- tempo médio de resposta de 343 ms;
- **incidente:** entre 14h11 e 15h03, o endpoint `/pedidos` retornou erro 500 seis vezes, com respostas de cerca de 2 a 3 segundos (mesmo as respostas bem-sucedidas desse período ficaram lentas); a partir de 15h24 ele voltou ao normal.

**Como cada passo se liga aos conceitos:**

| Passo | Conceito |
|---|---|
| Mostrar o CSV | Fonte de dados |
| Upload a file | Ingestão: o CSV vira o **índice** `acessos`, cada linha um **documento**, cada coluna um **campo** com tipo |
| Discover | Explorar os documentos dentro de um intervalo de tempo, pelo **Data View** |
| Filtro KQL `status_code >= 500` | Encontrar uma situação específica (os 6 erros) |
| Lens | Transformar um campo em gráfico (endpoints mais acessados) |
| Dashboard | Reunir as visualizações; um clique filtra todos os painéis |
