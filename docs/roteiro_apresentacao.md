# Roteiro da apresentação (≈ 16 minutos)

Apoio para uma fala natural, não um texto para decorar. O limite da avaliação é de 7 a 20 minutos; o plano abaixo fica em cerca de 16 minutos, com folga nos dois sentidos. Os números dos slides seguem `slides/seminario_kibana.pptx`, e as notas do apresentador de cada slide repetem estes pontos.

## Visão geral

| Bloco | Slides | Tempo | Acumulado |
|---|---|---|---|
| Abertura e problema | 1–2 | 1 min 40 s | 1:40 |
| Kibana, Elasticsearch e conceitos | 3–5 | 3 min 20 s | 5:00 |
| Logstash e arquitetura | 6–7 | 2 min 30 s | 7:30 |
| Preparação da demonstração | 8 | 1 min | 8:30 |
| Demonstração ao vivo | 9 | 5 min | 13:30 |
| Vantagens, limitações e usos | 10–11 | 1 min 50 s | 15:20 |
| Conclusão | 12 | 40 s | ≈ 16:00 |

**Divisão sugerida:** uma pessoa conduz os slides 1 a 8 enquanto a outra confere o ambiente; na demonstração, quem preparou o ambiente opera o computador e a outra pessoa narra; os slides 10 a 12 podem ser divididos entre as duas.

**Se o tempo apertar:** pular o passo do clique no dashboard e resumir os slides 4 e 5.

## Slide a slide

### 1. Kibana (0:00–0:20)
- Apresentar o tema e o grupo.
- "Vamos transformar eventos reais do Windows em respostas visuais."

### 2. O problema (0:20–1:40)
- O Windows registra eventos o tempo todo; no computador de testes, cerca de 440 por dia só no canal Aplicativo.
- No Visualizador de Eventos, a leitura é evento a evento: quantos erros? de quais aplicativos? quando?
- **Transição:** "precisamos coletar, guardar e visualizar."

### 3. O que é o Kibana (1:40–2:40)
- Elasticsearch armazena e pesquisa; Kibana é a interface web para explorar e visualizar.
- O Kibana não guarda os dados analisados: cada gráfico é uma consulta.
- Toda a stack na mesma versão (9.5.5 na demo).

### 4. Como os eventos ficam no Elasticsearch (2:40–3:50)
- Uma linha do arquivo JSON Lines vira um documento no índice `windows-events`.
- Índice = conjunto de documentos; documento = um evento; campo = cada atributo, com tipo.
- O tipo importa: `keyword` para agrupar e filtrar, `date` para a linha do tempo.

### 5. As ferramentas do Kibana (3:50–5:00)
- Data View aponta para o índice e o campo de tempo; Discover explora; Lens cria gráficos; Dashboard reúne tudo.
- KQL: `log.level : "Error"`.

### 6. Logstash (5:00–6:20)
- Pipeline em três estágios: entrada, filtro, saída.
- Na demo: entrada `file` com codec `json`, filtro que remove campos técnicos, saída para o Elasticsearch.
- ID estável por evento: reler o arquivo não duplica documentos.

### 7. Arquitetura da demonstração (6:20–7:30)
- No Windows: Event Log → coletor PowerShell (a cada 15 s) → `eventos.jsonl`.
- No Docker: Logstash → Elasticsearch → Kibana.
- O coletor fica fora do Docker porque lê o log do próprio computador.

### 8. Nossa demonstração (7:30–8:30)
- O que coletamos (horário, nível, provedor, ID) e o que fica de fora (mensagem, usuário, nome do computador).
- Amostra inicial de 7 dias e verificação a cada 15 s; os números variam conforme o computador.
- Pergunta-guia: "o que o próprio Windows registrou nesta semana?"

### 9. Demonstração prática (8:30–13:30)
- Seguir [roteiro_demonstracao.md](roteiro_demonstracao.md), seção 3.
- Ao final, ligar cada passo aos conceitos dos slides 4 a 7.

### 10. Vantagens (13:30–14:20)
- Sem código; integração nativa; ingestão flexível com o Logstash; interatividade; essencial gratuito; portabilidade.

### 11. Limitações e exemplos de uso (14:20–15:20)
- Limitações: três serviços e mais memória; coleta a cada 15 s (não instantânea); só metadados do canal Aplicativo, por privacidade; segurança desligada só por didática; solução local, não de produção.
- Usos: suporte e TI, monitoramento de logs, segurança (SIEM), vários computadores com agentes.

### 12. Conclusão e referências (15:20–16:00)
- Logstash prepara, Elasticsearch guarda, Kibana mostra.
- Na demo: dados reais deste computador, coletados automaticamente e sem mensagens ou dados pessoais.
- Referências oficiais da Elastic e da Microsoft; abrir para perguntas.

## Perguntas prováveis

| Pergunta | Resposta curta |
|---|---|
| Qual a diferença entre Logstash, Elasticsearch e Kibana? | O Logstash coleta e prepara, o Elasticsearch armazena e pesquisa, o Kibana mostra. |
| Por que um coletor em PowerShell, e não o Logstash lendo o Windows direto? | O coletor roda no Windows e lê o log de eventos com `Get-WinEvent`; o Logstash roda no Docker e lê o arquivo gerado. Em produção, a Elastic oferece o Elastic Agent para coletar de cada computador [1]. |
| Os eventos aparecem em tempo real? | Quase: o coletor verifica a cada 15 s e o Logstash lê o arquivo em seguida. Não é instantâneo. |
| Que dados saem do computador? | Só metadados: horário, nível, provedor, ID e número do evento. Mensagens, usuário e nome do computador ficam de fora, e os eventos não vão para o Git. |
| E se o coletor ou o Logstash relerem eventos? | Cada evento tem um ID estável; o Elasticsearch sobrescreve o mesmo documento, sem duplicar. |
| Por que a segurança foi desligada? | Para simplificar a demo local. A Elastic não recomenda desligar [22]; as portas só aceitam acesso da própria máquina. |
| O Kibana é gratuito? | Tudo o que usamos funciona na licença gratuita (*Basic*); alguns recursos avançados são pagos [26]. |
| E outras ferramentas, como Grafana ou Power BI? | Também visualizam dados; o diferencial do Kibana é ser a interface nativa do Elasticsearch e das soluções da Elastic. Uma comparação detalhada está fora do escopo deste seminário. |
