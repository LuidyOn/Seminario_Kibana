# Roteiro da apresentação (≈ 14 minutos)

Apoio para uma fala natural, não um texto para decorar. O limite da avaliação é de 7 a 20 minutos; o plano abaixo deixa folga nos dois sentidos. Os números dos slides seguem `slides/seminario_kibana.pptx`, e as notas do apresentador de cada slide repetem estes pontos.

## Visão geral

| Bloco | Slides | Tempo | Acumulado |
|---|---|---|---|
| Abertura e problema | 1–2 | 1 min 40 s | 1:40 |
| O que é o Kibana e conceitos | 3–5 | 3 min 20 s | 5:00 |
| Arquitetura | 6 | 1 min | 6:00 |
| Preparação da demonstração | 7 | 1 min | 7:00 |
| Demonstração ao vivo | 8 | 5 min | 12:00 |
| Vantagens, limitações e usos | 9–10 | 1 min 50 s | 13:50 |
| Conclusão | 11 | 40 s | ≈ 14:30 |

**Divisão sugerida:** uma pessoa conduz os slides 1 a 7 enquanto a outra confere o Kibana; na demonstração, quem preparou o ambiente opera o Kibana e a outra pessoa narra; os slides 9 a 11 podem ser divididos entre as duas.

**Se o tempo apertar:** pular o passo opcional da demonstração (clique na barra das 14h) e resumir os slides 4 e 5.

## Slide a slide

### 1. Kibana (0:00–0:20)
- Apresentar o tema e o grupo.
- "Vamos mostrar como transformar logs em respostas visuais."

### 2. O problema (0:20–1:40)
- Logs crescem rápido: cada requisição vira uma linha.
- Ler linha a linha não responde: quantos erros? quando? onde? ficou lento?
- Precisamos guardar de forma pesquisável e visualizar. **Transição:** "é aqui que entram o Elasticsearch e o Kibana."

### 3. O que é o Kibana (1:40–2:40)
- Elasticsearch armazena e pesquisa; Kibana é a interface web para explorar e visualizar.
- O Kibana não guarda os dados analisados: cada gráfico é uma consulta ao Elasticsearch.
- Os dois precisam estar na mesma versão (9.5.5 na demo).

### 4. Como os dados são organizados (2:40–3:50)
- Mostrar a linha do CSV virando um documento JSON.
- Índice = conjunto de documentos (`acessos`); documento = uma requisição; campo = cada chave, com tipo.
- O tipo importa: média só com número, linha do tempo só com data.

### 5. As ferramentas do Kibana (3:50–5:00)
- Data View: diz ao Kibana qual índice usar e qual é o campo de tempo.
- Discover: explorar e filtrar documentos. Lens: arrastar um campo e obter um gráfico. Dashboard: reunir tudo, com filtros compartilhados.

### 6. Arquitetura básica (5:00–6:00)
- CSV → Elasticsearch (porta 9200) → Kibana (porta 5601) → navegador.
- Tudo local, em containers, com `docker compose up -d`.
- Em produção, os dados chegariam por Elastic Agent, Logstash ou APIs; aqui usamos o *Upload a file* do Kibana.

### 7. Nossa demonstração (6:00–7:00)
- 70 requisições fictícias de uma loja virtual, em 01/10/2026, das 08h às 18h.
- Status 200, 401, 404 e 500; tempo de resposta em ms.
- Pergunta-guia: "o que aconteceu com a aplicação nesse dia?" (não revelar o incidente ainda).

### 8. Demonstração prática (7:00–12:00)
- Seguir [roteiro_demonstracao.md](roteiro_demonstracao.md), seção 2.
- Ao final, voltar aos slides ligando o que foi visto aos conceitos dos slides 4 e 5.

### 9. Vantagens (12:00–12:50)
- Sem código; integração nativa; interatividade; prototipação rápida com o Lens; essencial gratuito; dashboards exportáveis.

### 10. Limitações e exemplos de uso (12:50–13:50)
- Limitações: depende do Elasticsearch; consome memória; curva de aprendizado; segurança exige configuração (desligada aqui só por didática); recursos avançados pagos.
- Usos: logs de aplicações (nosso caso), segurança (logins negados, SIEM), infraestrutura, indicadores de negócio.

### 11. Conclusão e referências (13:50–14:30)
- Kibana = camada visual do Elasticsearch: do dado bruto ao dashboard sem programar.
- Na demo: 70 linhas de CSV viraram um dashboard que revelou um incidente às 14h.
- Referências oficiais da Elastic; abrir para perguntas.

### 12. Apoio (só se necessário)
- Captura do dashboard esperado, para usar se a demonstração ao vivo e o vídeo falharem.

## Perguntas prováveis

| Pergunta | Resposta curta |
|---|---|
| Qual a diferença entre Kibana e Elasticsearch? | O Elasticsearch armazena e pesquisa; o Kibana é a interface que consulta o Elasticsearch e mostra os resultados. |
| O Kibana guarda os dados? | Não. Os dados ficam no Elasticsearch; até os dashboards e Data Views ficam em índices do Elasticsearch (`.kibana_*`). |
| Por que a segurança foi desligada? | Para simplificar a demo local. A Elastic não recomenda desligar [14]; em produção, usam-se usuários, senhas e TLS. Aqui as portas só aceitam acesso da própria máquina. |
| Por que existe `@timestamp` se o CSV tem `timestamp`? | O *Upload a file* criou `@timestamp`, padrão do ecossistema Elastic, a partir da coluna `timestamp`; ele é o campo de tempo do Data View. |
| É preciso programar? | Não para Discover, Lens e Dashboard. A KQL é uma linguagem simples de filtro. |
| O Kibana é gratuito? | Tudo o que usamos funciona na licença gratuita (*Basic*). Alguns recursos avançados são pagos [17]. |
| Como os dados chegariam em produção? | Por Elastic Agent, Logstash ou APIs. O *Upload a file* é para exploração inicial [9]. |
| Por que o índice aparece como `yellow`? | Com um único nó, a réplica não tem onde ficar. É esperado neste ambiente. |
| E outras ferramentas, como Grafana ou Power BI? | Também visualizam dados; o diferencial do Kibana é ser a interface nativa do Elasticsearch e das soluções da Elastic. Uma comparação detalhada está fora do escopo deste seminário. |
