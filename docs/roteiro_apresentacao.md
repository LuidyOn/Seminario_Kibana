# Roteiro da apresentação (≈ 16 minutos)

Apoio para uma fala natural, não um texto para decorar. O limite da avaliação é de 7 a 20 minutos; o plano abaixo fica em cerca de 16 minutos, com folga nos dois sentidos. Os números dos slides seguem `slides/seminario_kibana.pptx`, e as notas do apresentador de cada slide repetem estes pontos.

## Visão geral

| Bloco | Slides | Tempo | Acumulado |
|---|---|---|---|
| Abertura e problema | 1–2 | 1 min 40 s | 1:40 |
| Kibana, Elasticsearch e conceitos | 3–5 | 3 min 20 s | 5:00 |
| Arquitetura e Logstash | 6–7 | 2 min 30 s | 7:30 |
| Dados reais e privacidade | 8 | 1 min | 8:30 |
| Demonstração ao vivo | 9 | 5 min | 13:30 |
| Vantagens, limitações e usos | 10–11 | 1 min 50 s | 15:20 |
| Referências e conclusão | 12–13 | 40 s | ≈ 16:00 |

Uma pessoa pode conduzir os slides 1 a 8 enquanto a outra confere o ambiente. Durante a demonstração, uma opera o computador e a outra narra. O grupo pode dividir os slides 10 a 13.

**Se o tempo apertar:** pular o passo do clique no dashboard e resumir os slides 4 e 5.

## Slide a slide

### 1. Kibana na prática (0:00–0:20)
- Apresentar o tema e o grupo.
- "Vamos transformar eventos reais do Windows em respostas visuais."

### 2. Análise de eventos do Windows (0:20–1:40)
- No computador de testes, o canal Aplicativo registrou cerca de 440 eventos em 24 horas em 29/10/2026.
- No Visualizador de Eventos, a leitura é evento a evento: quantos erros? de quais aplicativos? quando?
- **Transição:** "precisamos coletar, guardar e visualizar."

### 3. O que é o Kibana (1:40–2:40)
- Elasticsearch armazena e pesquisa; Kibana é a interface web para explorar e visualizar.
- O Kibana não guarda os dados analisados: cada gráfico é uma consulta.
- Toda a stack na mesma versão (9.5.5 na demo).

### 4. Documentos e índices (2:40–3:50)
- Uma linha do arquivo JSON Lines vira um documento no índice `windows-events`.
- Índice = conjunto de documentos; documento = um evento; campo = cada atributo, com tipo.
- Use `keyword` para agrupar e filtrar, `date` para a linha do tempo e `long` para números inteiros. A releitura atualiza o documento de mesmo ID.

### 5. Ferramentas do Kibana (3:50–5:00)
- Data View aponta para o índice e o campo de tempo; Discover explora; Lens cria gráficos; Dashboard reúne tudo.
- KQL: `log.level : "Error"`.

### 6. Arquitetura da demonstração (5:00–6:10)
- No Windows: Event Log → coletor PowerShell (a cada 15 s) → `eventos.jsonl`.
- No Docker, o Logstash lê o JSONL e envia os eventos ao Elasticsearch. O Kibana consulta o Elasticsearch.
- O coletor fica fora do Docker porque lê o log do próprio computador.

### 7. Pipeline do Logstash (6:10–7:30)
- A entrada `file` usa o codec `json`. O `sincedb` guarda a posição de leitura.
- O filtro `mutate` remove campos técnicos. A saída grava no índice `windows-events` com um ID estável por evento.
- A ingestão acompanha o arquivo continuamente, enquanto o coletor verifica o Windows em ciclos.

### 8. Dados reais e privacidade (7:30–8:30)
- O que coletamos (horário, nível, provedor, ID) e o que fica de fora (mensagem, usuário, nome do computador).
- Amostra inicial de 7 dias e verificação a cada 15 s; os números variam conforme o computador.
- Horário e provedor podem revelar contexto. A pasta `runtime/` fica fora do Git.
- Pergunta-guia: "o que o próprio Windows registrou nesta semana?"

### 9. Demonstração prática (8:30–13:30)
- Usar o [guia rápido no README](../README.md#demonstração-prática--guia-rápido-5-minutos) ou a seção 3 do [roteiro detalhado](roteiro_demonstracao.md).
- Ao final, ligar cada passo aos conceitos dos slides 4 a 7.

### 10. Vantagens (13:30–14:20)
- Visualização sem programação no Kibana. A coleta e a ingestão usam scripts e configurações.
- Integração nativa com o Elasticsearch, ingestão flexível, filtros interativos, licença Basic e portabilidade.

### 11. Limitações e casos de uso (14:20–15:20)
- Três serviços consomem mais memória. A coleta verifica apenas o canal Aplicativo a cada 15 s e exporta metadados.
- A configuração sem autenticação ou TLS serve somente para a demonstração local. Em produção, configure a segurança.
- Usos: suporte e TI, monitoramento de logs, segurança (SIEM), vários computadores com agentes.

### 12. Referências (15:20–15:35)
- Citar a documentação oficial da Elastic e da Microsoft. A [lista completa](referencias.md) acompanha os materiais.

### 13. Conclusão (15:35–16:00)
- O Windows fornece os eventos do canal Aplicativo.
- O Logstash prepara os registros e o Elasticsearch os indexa.
- O Kibana permite investigar os dados com filtros e gráficos. Abrir para perguntas.

## Perguntas prováveis

| Pergunta | Resposta curta |
|---|---|
| Qual a diferença entre Logstash, Elasticsearch e Kibana? | O Logstash coleta e prepara, o Elasticsearch armazena e pesquisa, o Kibana mostra. |
| Por que um coletor em PowerShell, e não o Logstash lendo o Windows direto? | O coletor roda no Windows e lê o log de eventos com `Get-WinEvent`; o Logstash roda no Docker e lê o arquivo gerado. Em produção, a Elastic oferece o Elastic Agent para coletar de cada computador [1]. |
| Os eventos aparecem em tempo real? | Quase: o coletor verifica a cada 15 s e o Logstash lê o arquivo em seguida. Não é instantâneo. |
| Que dados entram na pipeline? | Horário, nível, provedor, ID, número do evento e identificador aleatório da instalação. Mensagens, usuário e nome do computador ficam de fora. A coleta fica no computador. |
| E se o coletor ou o Logstash relerem eventos? | Cada evento tem um ID estável; o Elasticsearch sobrescreve o mesmo documento, sem duplicar. |
| Por que a segurança foi desligada? | Para simplificar a demo local. A Elastic não recomenda desligar [22]; as portas só aceitam acesso da própria máquina. |
| O Kibana é gratuito? | Tudo o que usamos funciona na licença gratuita (*Basic*); alguns recursos avançados são pagos [26]. |
| E outras ferramentas, como Grafana ou Power BI? | Também visualizam dados; o diferencial do Kibana é ser a interface nativa do Elasticsearch e das soluções da Elastic. Uma comparação detalhada está fora do escopo deste seminário. |
