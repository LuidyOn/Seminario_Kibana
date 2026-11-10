export const presenters = {
  luiz: { name: 'Luiz Oliveira', label: 'Luiz', part: 'Ímpares e demonstração', first: 1 },
  yahn: { name: 'Yahn Freitas', label: 'Yahn', part: 'Pares e conclusão', first: 2 },
} as const

export type Presenter = keyof typeof presenters
export type Scope = 'all' | Presenter

export const stages = [
  { name: 'Situação-problema', first: 1 },
  { name: 'Coleta', first: 3 },
  { name: 'Ingestão', first: 5 },
  { name: 'Indexação', first: 6 },
  { name: 'Investigação', first: 7 },
  { name: 'Demonstração', first: 11 },
  { name: 'Conclusão', first: 12 },
] as const

export type Slide = {
  id: number
  title: string
  seconds: number
  summary: string
  shows: string
  concepts: ReadonlyArray<{ term: string; explanation: string }>
  cues: readonly string[]
  speech: readonly string[]
  practice: string
  transition: string
  question: { prompt: string; answer: string; extension?: string }
  capture?: 'eventViewer' | 'discover' | 'dashboard'
  example?: string
}

const content: Slide[] = [
  {
    id: 1,
    title: 'Kibana',
    seconds: 25,
    summary: 'Abra com uma pergunta de suporte e apresente a dupla. O laboratório é hipotético e a demonstração usa eventos reais.',
    shows: 'A capa apresenta Luiz Oliveira e Yahn Freitas e antecipa o tema dos eventos do Windows analisados com Logstash, Elasticsearch e Kibana.',
    concepts: [
      { term: 'Pergunta de investigação', explanation: 'Comece com três pistas observáveis. Quando a falha apareceu, quantas vezes voltou e quais fontes a registraram?' },
      { term: 'Cenário e evidência', explanation: 'O laboratório organiza a narrativa. A evidência da demonstração vem do canal Aplicativo do computador da apresentação.' },
    ],
    cues: ['Imaginem o suporte de um laboratório', 'Quando, quantas vezes, quais fontes?', 'Luiz e Yahn'],
    speech: [
      'Imaginem que vocês cuidam do suporte de um laboratório. Alguns aplicativos começam a falhar. Vocês ainda precisam descobrir quando isso começou, quantas vezes aconteceu e quais componentes aparecem nos registros. Como vocês investigariam?',
      'Nós somos Luiz e Yahn. Vamos mostrar um caminho usando eventos reais do Windows.',
    ],
    practice: 'A pergunta de abertura volta no Discover. O intervalo ajuda a localizar o período, e os campos de nível e provedor ajudam a recortar os registros.',
    transition: 'Yahn, vamos começar pelo que o próprio Windows já registra.',
    question: {
      prompt: 'O caso do laboratório aconteceu no computador da demonstração?',
      answer: 'O laboratório é um cenário hipotético. A demonstração usa eventos reais do canal Aplicativo, gerados pelo computador em uso.',
    },
  },
  {
    id: 2,
    title: 'Aplicativos começaram a falhar',
    seconds: 65,
    summary: 'Mostre horário, nível, fonte e ID na lista do canal Aplicativo. Investigar frequência exige olhar o conjunto.',
    shows: 'A captura do Visualizador de Eventos fica ao lado das perguntas sobre início, frequência e fontes das falhas. O painel com mensagens está oculto.',
    capture: 'eventViewer',
    concepts: [
      { term: 'Canal Aplicativo', explanation: 'Reúne eventos registrados por aplicativos e serviços. O Visualizador também lista outros canais, como Sistema e Segurança.' },
      { term: 'Horário, nível, fonte e ID', explanation: 'O horário situa o registro, o nível indica a gravidade, a fonte identifica o provedor e o ID identifica o tipo de evento naquele contexto.' },
      { term: 'Volume de registros', explanation: 'O roteiro cita cerca de 440 eventos em 24 horas, medidos em 29/10/2026 no PC de teste. A captura e a medição têm seus próprios recortes.' },
    ],
    cues: ['Aponte as quatro colunas', 'Cenário hipotético, captura real', 'Como achar um pico na lista?'],
    speech: [
      'Por onde vocês começariam? Aqui o Windows já mostra horário, fonte, nível e ID. Esta captura é real. A história do laboratório é o cenário que usamos para levantar as perguntas.',
      'Agora imaginem passar por cada linha para saber se houve um pico. Num teste de 29 de outubro, vimos cerca de 440 eventos em 24 horas só no canal Aplicativo. Para comparar horários e frequências, precisamos pesquisar o conjunto.',
    ],
    practice: 'Abra Logs do Windows → Aplicativo no Visualizador de Eventos. Aponte as colunas com as mensagens ocultas e depois compare com a tabela do Discover.',
    transition: 'Luiz, como transformamos essa lista em dados que conseguimos pesquisar?',
    question: {
      prompt: 'Por que usar o Kibana se o Windows já tem um Visualizador de Eventos?',
      answer: 'O Visualizador permite consultar os registros na origem. No Kibana podemos combinar período e nível, agrupar por provedor e comparar distribuições em gráficos.',
    },
  },
  {
    id: 3,
    title: 'Dos registros ao painel',
    seconds: 75,
    summary: 'Siga um evento pelo diagrama. Windows e PowerShell geram o arquivo, Logstash o lê, Elasticsearch indexa e Kibana consulta.',
    shows: 'O diagrama separa Windows e containers Docker e desenha setas de consulta e resposta entre Kibana e Elasticsearch.',
    concepts: [
      { term: 'No Windows', explanation: 'O canal Aplicativo registra o evento. O PowerShell usa Get-WinEvent e acrescenta um objeto por linha ao arquivo eventos.jsonl.' },
      { term: 'Nos containers', explanation: 'O Logstash acompanha o arquivo montado, prepara o evento e o envia ao Elasticsearch. O Kibana oferece a interface no navegador. Os três serviços usam 9.5.5 neste projeto.' },
      { term: 'Gravação e consulta', explanation: 'O documento segue do Logstash ao Elasticsearch. Quando você abre o Discover, o Kibana pede resultados ao Elasticsearch e mostra a resposta.' },
      { term: 'Onde verificar', explanation: 'A API de Elasticsearch responde na porta local 9200, e o Kibana na 5601. O Logstash comunica-se pela rede do Docker.' },
    ],
    cues: ['Trace um evento da esquerda para a direita', 'Separe Windows e Docker', 'A seta de consulta sai do Kibana'],
    speech: [
      'Vamos acompanhar um evento. No próprio Windows, o PowerShell lê o canal Aplicativo e grava o JSONL. Do lado do Docker, o Logstash lê esse arquivo e prepara o evento para o Elasticsearch.',
      'O documento fica no Elasticsearch. Quando abrimos um painel, a comunicação vai nos dois sentidos. O Kibana pede dados, o Elasticsearch pesquisa e devolve o resultado, e o Kibana apresenta a resposta. Aqui os três serviços usam a mesma versão, 9.5.5.',
    ],
    practice: 'Mostre uma linha do JSONL para localizar a fronteira Windows/Docker. Depois abra a contagem do índice na porta 9200 e troque para o Kibana na 5601.',
    transition: 'Yahn, a primeira passagem acontece no Windows. Mostra como o coletor sabe de onde continuar?',
    question: {
      prompt: 'Por que usar PowerShell para ler os eventos?',
      answer: 'O coletor roda no Windows e usa Get-WinEvent para acessar o canal Aplicativo. O Logstash do projeto roda em um container Linux e recebe os eventos pelo arquivo compartilhado.',
      extension: 'Em outras arquiteturas, um agente no computador, como o Elastic Agent, pode fazer a coleta e enviar os dados à stack.',
    },
  },
  {
    id: 4,
    title: 'Coleta dos eventos',
    seconds: 70,
    summary: 'O PowerShell consulta o canal Aplicativo a cada 15 s, retoma pelo RecordId e acrescenta um objeto JSON por linha.',
    shows: 'O slide destaca os 15 segundos e encadeia canal Aplicativo, checkpoint e JSONL. Os metadados selecionados aparecem ao lado dos campos excluídos.',
    concepts: [
      { term: 'Amostra inicial', explanation: 'Sem checkpoint, o coletor carrega até 2.000 eventos dos últimos sete dias do canal Aplicativo.' },
      { term: 'RecordId e checkpoint', explanation: 'O RecordId é o número do registro no canal. O checkpoint do PowerShell guarda o último RecordId exportado e permite buscar os registros posteriores, mesmo quando dois horários coincidem.' },
      { term: 'Metadados selecionados', explanation: 'Horário UTC, canal, provedor, códigos, RecordId, nível e um identificador aleatório da instalação. Mensagem, usuário e nome da máquina ficam fora. Horário e provedor ainda podem revelar contexto.' },
    ],
    cues: ['Até 2.000 na primeira leitura', '15 s e RecordId', 'Uma linha por evento, mensagens fora'],
    speech: [
      'Na primeira execução, buscamos até dois mil eventos dos últimos sete dias. Depois o PowerShell verifica o canal Aplicativo a cada quinze segundos e consulta os registros com RecordId acima do último que exportou. Esse número fica no checkpoint.',
      'Cada evento novo vira uma linha JSON. Levamos horário, nível, provedor e identificadores, incluindo um código aleatório da instalação. Mensagem, usuário e nome do computador ficam de fora. A coleta fica na máquina, porque até o horário e o provedor podem revelar contexto.',
    ],
    practice: 'Mostre o fim de runtime/logs/eventos.jsonl no terminal. Aponte horário, nível e ID. O checkpoint do coletor fica em runtime/state/checkpoint.json.',
    transition: 'Luiz, o arquivo já existe. Quem acompanha as novas linhas?',
    question: {
      prompt: 'Se dois eventos tiverem o mesmo horário, como a coleta sabe onde retomar?',
      answer: 'Ela se orienta pelo RecordId no canal. No próximo ciclo, procura registros com número acima do checkpoint.',
      extension: 'Se o canal for limpo ou se registros expirarem no log circular, o coletor pode detectar a situação e registrar um aviso. Registros já descartados pelo Windows podem ficar fora da coleta.',
    },
  },
  {
    id: 5,
    title: 'Logstash',
    seconds: 75,
    summary: 'O Logstash acompanha o JSONL. Input lê e decodifica, filter limpa os campos técnicos e output grava com um ID estável.',
    shows: 'Três blocos apresentam input, filter e output. Na base do slide, sincedb e document_id explicam a retomada da leitura e a identidade do documento.',
    concepts: [
      { term: 'Input e codec', explanation: 'O plugin file segue as linhas novas do arquivo no modo tail. Como ele já entrega uma linha por vez, o codec json converte cada linha em evento.' },
      { term: 'Filter', explanation: 'O mutate remove campos técnicos acrescentados pelo próprio Logstash, como @version e o caminho do arquivo.' },
      { term: 'Output e document_id', explanation: 'A saída envia ao índice windows-events e usa event.id como document_id. O coletor forma esse ID com canal, RecordId e horário. Reenviar o mesmo ID atualiza o documento correspondente.' },
      { term: 'Sincedb e checkpoint', explanation: 'O sincedb guarda a posição de leitura no arquivo. O checkpoint guarda o último RecordId exportado do Windows. Cada estágio retoma em seu próprio ponto.' },
    ],
    cues: ['Input → filter → output', 'Sincedb é posição no arquivo', 'Mesmo ID, mesmo documento'],
    speech: [
      'O Logstash acompanha o arquivo. Na entrada, o plugin file separa as linhas e o codec json decodifica cada uma. O sincedb guarda a posição no arquivo. O checkpoint que o Yahn acabou de explicar pertence à leitura no Windows.',
      'No filtro, o mutate remove campos técnicos da ingestão. A saída grava no Elasticsearch com o ID do evento. Se o Logstash reler uma linha, o documento com aquele ID é atualizado. Para este volume, o heap do Logstash foi configurado em 256 megabytes.',
    ],
    practice: 'Abra logstash/pipeline/windows-events.conf. Mostre file e codec, mutate e document_id, nessa ordem. A leitura do arquivo segue em execução entre os ciclos de coleta.',
    transition: 'Yahn, o evento chegou ao Elasticsearch. Como ele fica organizado para consulta?',
    question: {
      prompt: 'Se o Logstash perder a posição de leitura, a contagem dobra?',
      answer: 'Uma releitura pode reenviar eventos. Como a saída grava no mesmo índice com o mesmo document_id, cada documento é atualizado e a releitura por si só não aumenta a contagem.',
      extension: 'O JSONL pode conter linhas repetidas após uma falha entre exportar e salvar o checkpoint. Para comparar arquivo e índice, confira os IDs únicos depois que o Logstash terminar.',
    },
  },
  {
    id: 6,
    title: 'Elasticsearch',
    seconds: 70,
    summary: 'O índice windows-events reúne documentos JSON. O mapeamento dá tipos aos campos usados na busca e na análise.',
    shows: 'Um exemplo parcial do JSON aparece junto às definições de índice, documento e campo. A base do slide retoma o efeito do ID estável.',
    example: '{\n  "@timestamp": "2026-10-29T14:05:12.000Z",\n  "event": {"code": "1000"},\n  "log": {"level": "Error"},\n  "winlog": {"record_id": 50123}\n}',
    concepts: [
      { term: 'Índice e documento', explanation: 'windows-events é o índice consultado na demo. Cada documento JSON representa um evento e tem um identificador.' },
      { term: 'Mapeamento', explanation: 'O template define @timestamp como date, nível e código como keyword, e winlog.record_id como long. Assim o tempo vira eixo do histograma e os níveis viram categorias.' },
      { term: 'Agregação', explanation: 'O Elasticsearch pode contar documentos por nível ou agrupá-los por intervalo de tempo para alimentar os gráficos.' },
    ],
    cues: ['Um índice, vários documentos', 'date, keyword, long', 'Contagem na API'],
    speech: [
      'O índice windows-events reúne os documentos. Cada documento representa um evento em JSON. No exemplo, o horário tem tipo date, nível e código são keyword, e o número do registro é um inteiro long.',
      'Esses tipos ajudam a montar uma linha do tempo, filtrar o nível e agrupar por código. Quando chega um evento com o mesmo identificador, o Elasticsearch atualiza o documento correspondente.',
    ],
    practice: 'Abra a contagem de windows-events na porta 9200. O template do projeto está em logstash/windows-events-template.json e é instalado pelo Logstash.',
    transition: 'Luiz, com os documentos pesquisáveis, podemos voltar à pergunta sobre os erros da semana.',
    question: {
      prompt: 'Por que event.code tem tipo keyword se o código parece um número?',
      answer: 'Na investigação, ele representa uma categoria, como “1000”. A busca e o agrupamento usam o valor exato do código.',
      extension: 'winlog.record_id tem tipo long para representar um inteiro. O tipo de um campo acompanha o uso que fazemos dele.',
    },
  },
  {
    id: 7,
    title: 'O que é o Kibana',
    seconds: 55,
    summary: 'O Kibana oferece a interface para perguntar e explorar. A busca e as agregações são executadas no Elasticsearch.',
    shows: 'O slide pergunta “Que erros ocorreram nesta semana?” e divide o caminho da resposta em consulta e visualização no navegador.',
    concepts: [
      { term: 'Intervalo e filtro', explanation: 'No Discover, Last 7 days delimita o período e log.level : "Error" seleciona documentos com aquele nível.' },
      { term: 'Pesquisa e agregação', explanation: 'A busca encontra documentos compatíveis. Uma agregação resume os resultados, por exemplo contando quantos eventos ocorreram por provedor.' },
      { term: 'Persistência', explanation: 'Os eventos ficam no Elasticsearch. Objetos salvos do Kibana, como um Data View ou um dashboard, também persistem em índices do Elasticsearch.' },
    ],
    cues: ['Que erros ocorreram nesta semana?', 'Elasticsearch encontra e calcula', 'Kibana apresenta'],
    speech: [
      'Vamos voltar à pergunta sobre os erros. Quando escolho a última semana e filtro pelo nível no Kibana, o Elasticsearch busca os documentos e calcula os totais que os gráficos pedem.',
      'O Kibana apresenta o resultado no navegador como lista ou gráfico. Os eventos e os objetos que salvamos no Kibana ficam no Elasticsearch.',
    ],
    practice: 'No Discover, aplique Last 7 days e a KQL de erros. Veja a tabela de documentos e compare com o histograma de ocorrências no tempo.',
    transition: 'Yahn, mostra o percurso pelas ferramentas que vamos usar ao vivo?',
    question: {
      prompt: 'Onde ficam os eventos e onde fica o dashboard salvo?',
      answer: 'Os eventos ficam no índice windows-events do Elasticsearch. O dashboard é um objeto salvo do Kibana persistido em índices do próprio Elasticsearch.',
      extension: 'O NDJSON do projeto guarda as definições dos objetos salvos. As métricas dos painéis são calculadas sobre os documentos que o Elasticsearch encontra ao consultar.',
    },
  },
  {
    id: 8,
    title: 'Ferramentas do Kibana',
    seconds: 75,
    summary: 'Passe por Data View, Discover, KQL, Lens e Dashboard, com a captura real da busca por erros.',
    shows: 'Cinco ferramentas aparecem na ordem de uso. A captura mostra o Data View Eventos do Windows, a busca KQL por Error, o histograma e as colunas de documentos.',
    capture: 'discover',
    concepts: [
      { term: 'Data View', explanation: 'Eventos do Windows aponta para windows-events e usa @timestamp como campo de tempo.' },
      { term: 'Discover e KQL', explanation: 'O Discover permite ler registros e examinar a distribuição no tempo. KQL recorta a busca, como em log.level : "Error".' },
      { term: 'Lens e Dashboard', explanation: 'O Lens transforma um campo em gráfico. O dashboard reúne visualizações e permite aplicar os mesmos filtros aos quatro painéis originais da demo.' },
    ],
    cues: ['Selecione o Data View', 'Explore e filtre no Discover', 'Lens monta, Dashboard reúne'],
    speech: [
      'Primeiro escolho Eventos do Windows no Data View, que indica o índice e o campo de tempo. No Discover vejo os documentos, e com KQL posso reduzir a lista aos erros. Para incluir avisos, combino os dois níveis com or.',
      'O Lens usa um campo, como event.code, para montar um gráfico. Quando juntamos visualizações num dashboard, fica fácil comparar o que muda em todos os painéis com o mesmo filtro.',
    ],
    practice: 'No Discover, aplique log.level : "Error", confira o período, limpe a consulta e abra a prévia de event.code → Visualize.',
    transition: 'Luiz, o que esse percurso facilita para quem está investigando?',
    question: {
      prompt: 'Dá para obter uma contagem por nível usando apenas KQL?',
      answer: 'KQL seleciona quais documentos entram na consulta. Para contar por nível, configure uma agregação sobre log.level no Lens ou em uma consulta ao Elasticsearch.',
    },
  },
  {
    id: 9,
    title: 'Vantagens',
    seconds: 55,
    summary: 'Explore o que a interface facilita, o que a integração reaproveita e como outras fontes podem ampliar a análise.',
    shows: 'Quatro blocos destacam visualização sem programação, interatividade, integração e expansão. O slide indica o uso dos recursos Basic na demonstração.',
    concepts: [
      { term: 'Visualização pela interface', explanation: 'No Lens, escolha event.code e a contagem de documentos para montar um gráfico por código. A coleta e a ingestão continuam usando código e configuração.' },
      { term: 'Filtros compartilhados', explanation: 'Um clique em Error recorta os painéis juntos. Você pode comparar a frequência no tempo e os provedores sem reconstruir os gráficos.' },
      { term: 'Integração e expansão', explanation: 'A busca do Kibana é integrada ao Elasticsearch. O Logstash pode receber outras fontes por plugins. Em outra máquina, o repositório inicia a mesma estrutura com eventos locais.' },
      { term: 'Licença Basic', explanation: 'O percurso de Discover, KQL, Lens e Dashboard deste seminário funciona com os recursos da licença gratuita Basic.' },
    ],
    cues: ['Crie o gráfico pela interface', 'Um filtro, vários painéis', 'Configuração reaproveitável'],
    speech: [
      'Para investigar, vocês conseguem pesquisar, filtrar e criar gráficos pela interface. A coleta e a ingestão usam um script e uma configuração. O Elasticsearch executa a busca, e podemos adaptar as entradas e os filtros do Logstash para outras fontes.',
      'Em outro computador, o repositório coleta os eventos daquela máquina. Os recursos que vamos usar no Kibana estão na licença Basic.',
    ],
    practice: 'Use o Lens para mostrar a prévia do gráfico por ID. No dashboard, aplique um filtro por clique e mostre o efeito nos painéis.',
    transition: 'Yahn, quais cuidados entram quando saímos deste ambiente de demonstração?',
    question: {
      prompt: '“Sem programação” se aplica a todo o projeto?',
      answer: 'O gráfico e os filtros podem ser configurados na interface do Kibana. A coleta usa PowerShell e a ingestão usa a configuração do Logstash.',
    },
  },
  {
    id: 10,
    title: 'Limitações e aplicações',
    seconds: 65,
    summary: 'A demo tem três serviços, coleta em ciclos e escopo local. Autenticação e TLS fazem parte de uma instalação de produção.',
    shows: 'Uma coluna lista limites da demo e outra apresenta aplicações. A faixa inferior explicita a ausência de autenticação e TLS no ambiente didático.',
    concepts: [
      { term: 'Memória e manutenção', explanation: 'Neste volume, Elasticsearch e Logstash usam heaps de 512 MB e 256 MB, respectivamente. O consumo total também inclui Kibana, Docker e memória fora dos heaps.' },
      { term: 'Escopo local', explanation: 'Um computador, um nó e um canal do Windows. As portas escutam apenas no próprio computador e a segurança da stack foi simplificada para a aula.' },
      { term: 'Aplicações', explanation: 'A abordagem apoia suporte, observabilidade e centralização de logs. Uma solução de segurança usa fontes, permissões e controles apropriados ao ambiente.' },
    ],
    cues: ['Memória, intervalo, manutenção', 'Um nó local', 'Em produção, autenticação e TLS'],
    speech: [
      'São três serviços, então precisamos conferir memória. A coleta tem um intervalo e os componentes exigem manutenção. Nesta demonstração, tudo roda em um computador, com um nó e portas acessíveis só localmente.',
      'Simplificamos a segurança para mostrar o fluxo. Em produção, a configuração inclui autenticação e TLS. A mesma abordagem pode apoiar suporte, observabilidade, centralização de logs e segurança, com a arquitetura e as fontes adequadas.',
    ],
    practice: 'Antes da aula, confira os containers e a memória. Durante a fala, use as portas locais para explicar por que a stack fica no computador da apresentação.',
    transition: 'Luiz, vamos acompanhar o caminho da lista de eventos até o painel.',
    question: {
      prompt: 'O heap de 256 MB é o consumo total de memória do Logstash?',
      answer: 'Heap é a região de memória gerenciada pela JVM. O processo pode usar mais memória, e a stack também roda Elasticsearch, Kibana e Docker.',
      extension: 'Use docker stats --no-stream para observar o consumo por container. O README orienta ter cerca de 3 GB disponíveis no Windows, com o Docker Desktop aberto.',
    },
  },
  {
    id: 11,
    title: 'Demonstração prática',
    seconds: 300,
    summary: 'Luiz executa o percurso ao vivo em cerca de cinco minutos, do canal Aplicativo ao filtro por clique.',
    shows: 'O slide antecipa a tela ao vivo com uma captura histórica dos quatro painéis originais. A trilha embaixo indica origem, coleta, ingestão, exploração e dashboard.',
    capture: 'dashboard',
    concepts: [
      { term: 'Três ritmos', explanation: 'O PowerShell verifica o Windows a cada 15 s, o Logstash acompanha o JSONL continuamente e o dashboard refaz a consulta a cada 30 s. A chegada depende também da indexação e de haver novos eventos.' },
      { term: 'Contagens com escopos diferentes', explanation: 'O endpoint _count, sem filtros, conta os documentos no índice. No dashboard, período e filtros determinam o total mostrado.' },
      { term: 'Interação', explanation: 'A barra em Eventos por nível acrescenta um filtro de log.level aos painéis. O × remove o filtro e restaura a visão geral.' },
    ],
    cues: ['Fonte → coleta → JSONL', 'Pipeline → contagem → Discover', 'KQL → Lens → clique e ×'],
    speech: [
      'Vamos voltar ao canal Aplicativo. Mostro como retomamos a coleta no PowerShell, como fica uma linha no JSONL e o que o Logstash faz até entregar o documento ao Elasticsearch.',
      'Depois da contagem, abro o Discover e filtro os erros. No Lens, uso o ID de evento para montar um gráfico. No dashboard, vou clicar em uma barra para mostrar como o filtro afeta os painéis e depois removê-lo.',
    ],
    practice: 'Siga a preparação prévia e os oito cartões cronometrados da demonstração. A captura é uma referência visual, e os totais ao vivo variam conforme os dados e o período.',
    transition: 'Yahn, voltando à pergunta do laboratório, o que conseguimos descobrir a partir dos registros?',
    question: {
      prompt: 'Por que _count pode ser maior do que o total do dashboard?',
      answer: 'Sem consulta, _count conta todos os documentos do índice. O dashboard pode limitar a contagem aos últimos sete dias ou a um nível selecionado.',
      extension: 'Para comparar Discover e dashboard, coloque os dois no mesmo intervalo e retire consultas ou filtros que só estejam ativos em um deles.',
    },
  },
  {
    id: 12,
    title: 'Perguntas?',
    seconds: 30,
    summary: 'Volte à pergunta inicial, resuma os três papéis e abra o espaço de perguntas com Yahn.',
    shows: 'O slide organiza a conclusão em Windows, Logstash e Elasticsearch, e Kibana.',
    concepts: [
      { term: 'Origem', explanation: 'O Windows registra os eventos, e o PowerShell lê o canal Aplicativo.' },
      { term: 'Ingestão e busca', explanation: 'O Logstash prepara cada evento para o Elasticsearch, que torna os documentos pesquisáveis.' },
      { term: 'Leitura dos resultados', explanation: 'O Kibana ajuda a comparar períodos, frequências e fontes. A análise orienta os próximos passos da investigação.' },
    ],
    cues: ['Retome a pergunta do laboratório', 'Três papéis em uma frase', 'Abra para perguntas'],
    speech: [
      'Para investigar as falhas do laboratório, partimos dos registros do Windows. O Logstash prepara os eventos, o Elasticsearch permite encontrá-los e o Kibana ajuda a explorar os resultados.',
      'Assim podemos olhar quando os erros ocorreram, com que frequência e quais fontes aparecem. Perguntas?',
    ],
    practice: 'Deixe o slide de perguntas aberto. Se pedirem evidência, retome a consulta no Discover ou o gráfico por provedor do dashboard.',
    transition: 'Yahn abre a discussão e mantém a conclusão na tela. Use as fontes do seminário quando pedirem uma referência.',
    question: {
      prompt: 'Um pico em um provedor permite concluir a causa da falha?',
      answer: 'O pico indica onde investigar. Para confirmar a causa, vale correlacionar horário, código, provedor e outras evidências disponíveis.',
      extension: 'Neste projeto, a investigação com os gráficos usa metadados selecionados. Se uma análise precisar de mais contexto, avalie a fonte e suas permissões antes de acessar os detalhes.',
    },
  },
]

let start = 0
export const slides = content.map((slide) => {
  const presenter: Presenter = slide.id % 2 ? 'luiz' : 'yahn'
  const stage = stages.reduce<(typeof stages)[number]>(
    (current, entry) => slide.id >= entry.first ? entry : current,
    stages[0],
  )
  const timed = { ...slide, presenter, stage, start, end: start + slide.seconds }
  start = timed.end
  return timed
})

export type TimedSlide = (typeof slides)[number]
export const totalSeconds = start
