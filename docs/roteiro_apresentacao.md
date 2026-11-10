# Roteiro da apresentação (≈ 16 minutos)

A narrativa começa com uma situação hipotética de suporte. As telas e os dados da demonstração vêm do ambiente real do projeto. O plano usa 16 minutos dentro da janela de 7 a 20 minutos da avaliação.

| Bloco | Slides | Tempo | Acumulado |
|---|---|---:|---:|
| Abertura e situação-problema | 1–2 | 1 min 30 s | 1:30 |
| Arquitetura, coleta e ingestão | 3–5 | 3 min 40 s | 5:10 |
| Elasticsearch e exploração no Kibana | 6–8 | 3 min 20 s | 8:30 |
| Vantagens, limitações e aplicações | 9–10 | 2 min | 10:30 |
| Demonstração ao vivo | 11 | 5 min | 15:30 |
| Conclusão e perguntas | 12 | 30 s | 16:00 |

**Divisão sugerida.** Luiz conduz os slides 1 a 5. Yahn assume quando o evento chega ao Elasticsearch e apresenta os slides 6 a 10. Durante a demonstração, um opera o computador enquanto o outro narra. O grupo fecha com o slide 12 e deixa a tela de perguntas aberta.

## Slide a slide

### 1. Kibana (0:00–0:25)

“Imaginem que vocês cuidam do suporte de um laboratório. Alguns aplicativos começam a falhar, mas vocês ainda não sabem quando começou, quantas vezes aconteceu nem quais componentes estão envolvidos. Como vocês investigariam?”

Apresentar Luiz Oliveira e Yahn Freitas e passar para a fonte dos registros.

### 2. Aplicativos começaram a falhar (0:25–1:30)

Mostrar a captura real do canal Aplicativo. Apontar horário, nível, fonte e ID. Pedir à turma que imagine procurar um pico ou uma origem entre muitos registros. O cenário do laboratório é hipotético. A medição histórica de cerca de 440 eventos em 24 horas pertence ao computador de teste em 29/10/2026.

**Transição.** “Para responder a essas perguntas, precisamos conseguir pesquisar o conjunto de registros.”

### 3. Dos registros ao painel (1:30–2:45)

Seguir a trilha no slide. O Windows fornece os eventos. PowerShell e JSONL ficam no computador. Logstash, Elasticsearch e Kibana ficam nos containers. As setas de consulta e resposta mostram o papel do Elasticsearch e do Kibana.

**Transição.** “O primeiro passo é ler os eventos que o Windows já tem.”

### 4. Coleta dos eventos (2:45–3:55)

Mostrar a cadência de 15 segundos, a retomada pelo `RecordId` do checkpoint e a linha JSONL gerada para cada evento novo. Explicar quais metadados entram e por que mensagem, usuário e nome da máquina ficam fora.

**Transição.** “Agora que temos o arquivo, alguém precisa acompanhá-lo.”

### 5. Logstash (3:55–5:10)

Percorrer **Input → Filter → Output**. A entrada `file` com codec `json` lê o arquivo e o `sincedb` guarda a posição. O `mutate` remove campos técnicos. A saída envia ao Elasticsearch com o ID estável do evento.

**Passagem para o segundo apresentador.** “Agora o evento chegou ao Elasticsearch. Vamos ver como ele fica organizado para consulta.”

### 6. Elasticsearch (5:10–6:20)

No exemplo ilustrativo, apontar o documento, o índice `windows-events` e os campos. Relacionar `date` ao tempo, `keyword` a filtros e agrupamentos, e `long` ao número do registro.

**Transição.** “Com os documentos pesquisáveis, voltamos à pergunta sobre os erros da semana.”

### 7. O que é o Kibana (6:20–7:15)

Usar a pergunta “Que erros ocorreram nesta semana?”. O Kibana envia a consulta. O Elasticsearch pesquisa e agrega. A resposta aparece no navegador em uma lista ou gráfico.

**Transição.** “Este é o caminho que vamos repetir ao vivo no Kibana.”

### 8. Ferramentas do Kibana (7:15–8:30)

Acompanhar a sequência Data View, Discover, KQL, Lens e Dashboard. Na captura real, apontar o filtro `log.level : "Error"`. O Lens entra depois para transformar um campo em gráfico. O dashboard reúne as visualizações e compartilha os filtros.

**Transição.** “O que esse caminho facilita para quem está investigando?”

### 9. Vantagens (8:30–9:25)

Mostrar que gráficos e filtros podem ser configurados pela interface. A busca usa o Elasticsearch. A ingestão é flexível e pode receber outras fontes. Os recursos da demonstração funcionam na licença Basic.

**Transição.** “O que roda neste computador já mostra o fluxo, mas uma instalação de produção tem outras exigências.”

### 10. Limitações e aplicações (9:25–10:30)

Mencionar memória, intervalo de coleta, manutenção e escopo local. Explicar que em produção é preciso configurar autenticação e TLS. Dar exemplos de suporte, observabilidade, logs centralizados e segurança em soluções apropriadas.

**Transição.** “Agora vamos acompanhar esse processo funcionando.”

### 11. Demonstração prática (10:30–15:30)

Exibir a captura do dashboard imediatamente antes de alternar para o ambiente ao vivo. Executar uma única sequência, da origem ao dashboard. Usar o [guia rápido no README](../README.md#demonstração-prática--guia-rápido-5-minutos) ou a seção 3 do [roteiro detalhado](roteiro_demonstracao.md).

**Transição.** “Voltando à pergunta do laboratório, o que conseguimos descobrir a partir dos registros?”

### 12. Perguntas? (15:30–16:00)

Retomar a situação inicial. O Windows produz eventos reais. Logstash e Elasticsearch preparam e tornam esses registros pesquisáveis. O Kibana permite explorá-los com filtros e gráficos. Deixar o slide aberto para perguntas.

As fontes da Elastic e da Microsoft estão nas notas pertinentes e na [bibliografia completa](referencias.md).

## Perguntas prováveis

| Pergunta | Resposta curta |
|---|---|
| Qual a diferença entre Logstash, Elasticsearch e Kibana? | O Logstash lê o arquivo e prepara os eventos. O Elasticsearch armazena e pesquisa. O Kibana consulta e mostra a resposta. |
| Por que um coletor em PowerShell, e não o Logstash lendo o Windows direto? | O coletor roda no Windows e lê o log de eventos com `Get-WinEvent`; o Logstash roda no Docker e lê o arquivo gerado. Em produção, a Elastic oferece o Elastic Agent para coletar de cada computador [1]. |
| Os eventos aparecem em tempo real? | O coletor verifica a cada 15 s. Depois vêm a leitura do Logstash e a indexação no Elasticsearch. |
| Que dados entram na pipeline? | Horário, nível, provedor, ID, número do evento e identificador aleatório da instalação. Mensagens, usuário e nome do computador ficam de fora. A coleta fica no computador. |
| E se o coletor ou o Logstash relerem eventos? | Cada evento tem um ID estável; o Elasticsearch sobrescreve o mesmo documento, sem duplicar. |
| Por que a segurança foi desligada? | Para simplificar a demo local. A Elastic não recomenda desligar [22]; as portas só aceitam acesso da própria máquina. |
| O Kibana é gratuito? | Tudo o que usamos funciona na licença gratuita (*Basic*); alguns recursos avançados são pagos [26]. |
| E outras ferramentas, como Grafana ou Power BI? | Também visualizam dados; o diferencial do Kibana é ser a interface nativa do Elasticsearch e das soluções da Elastic. Uma comparação detalhada está fora do escopo deste seminário. |
