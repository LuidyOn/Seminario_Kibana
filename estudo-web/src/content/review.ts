export const flashcards = [
  { front: 'Quem prepara, quem armazena e quem apresenta?', back: 'Logstash prepara os eventos. Elasticsearch armazena, pesquisa e agrega. Kibana permite consultar e apresenta os resultados.' },
  { front: 'Qual canal alimenta a demonstração?', back: 'Application, chamado Aplicativo no Visualizador de Eventos. O coletor usa Get-WinEvent no próprio Windows.' },
  { front: 'Por que o arquivo é JSONL?', back: 'Cada linha contém um objeto JSON completo. O coletor pode acrescentar linhas e o Logstash pode acompanhar o arquivo.' },
  { front: 'Checkpoint e sincedb guardam a mesma posição?', back: 'O checkpoint guarda o último RecordId exportado do Windows. O sincedb guarda onde o Logstash parou de ler o JSONL.' },
  { front: 'O que acontece quando um evento é relido?', back: 'A saída usa o mesmo document_id no mesmo índice. O Elasticsearch atualiza o documento daquele evento.' },
  { front: 'O que o mutate remove na demo?', back: 'Campos técnicos acrescentados na ingestão, como @version e o caminho do arquivo. Os metadados selecionados do evento seguem ao índice.' },
  { front: 'Como se relacionam índice, documento e campo?', back: 'windows-events é o índice. Cada evento forma um documento JSON. log.level é um dos campos desse documento.' },
  { front: 'Por que mapear o horário como date?', back: 'Para consultar intervalos e agrupar no tempo. O Data View usa @timestamp como campo de tempo.' },
  { front: 'O que configura o Data View Eventos do Windows?', back: 'O índice windows-events e o campo temporal @timestamp que o Kibana usa para explorar e filtrar os eventos.' },
  { front: 'Como filtrar somente erros no Discover?', back: 'Use log.level : "Error" com o Data View Eventos do Windows. Os resultados também respeitam o intervalo de tempo.' },
  { front: 'Como ir do campo event.code ao Lens?', back: 'Limpe a consulta no Discover, abra a prévia de event.code e escolha Visualize.' },
  { front: 'O que muda ao clicar numa barra do dashboard?', back: 'Um filtro de log.level passa a recortar os painéis. Remova o filtro no × para voltar à visão geral.' },
  { front: 'O que mede cada relógio da demo?', back: '15 s entre verificações no Windows. O Logstash acompanha o arquivo continuamente. A cada 30 s o dashboard repete a consulta.' },
  { front: 'Por que _count e dashboard podem divergir?', back: '_count sem consulta conta todos os documentos do índice. O dashboard usa o período selecionado e os filtros ativos.' },
  { front: 'Quais cuidados de privacidade entram antes da demo?', back: 'Oculte o painel de mensagens, use os metadados selecionados e mantenha runtime/ local. Mesmo horários e provedores podem revelar contexto.' },
  { front: 'O que a configuração local simplifica?', back: 'Tudo roda numa máquina e em um nó, com portas locais e sem autenticação ou TLS. Em produção, configure segurança, capacidade e controles do ambiente.' },
]

type QuizQuestion = {
  slide: number
  question: string
  choices: readonly string[]
  correct: number
  explanation: string
}

export const quiz: QuizQuestion[] = [
  {
    slide: 1,
    question: 'Como apresentar o cenário do laboratório sem confundir a turma sobre a origem dos dados?',
    choices: [
      'Dizer que a captura comprova um incidente naquele laboratório.',
      'Apresentar o laboratório como hipótese e identificar o computador como fonte dos eventos reais.',
      'Usar a quantidade histórica da captura como meta para a execução ao vivo.',
    ],
    correct: 1,
    explanation: 'O cenário dá sentido à pergunta de investigação. A evidência exibida vem do canal Aplicativo do computador da demonstração.',
  },
  {
    slide: 2,
    question: 'Que recorte ajuda a investigar se uma fonte passou a registrar mais falhas?',
    choices: [
      'Ordenar o índice pelo RecordId e olhar apenas o número mais alto.',
      'Contar todos os eventos do índice em uma única métrica.',
      'Comparar ocorrências no tempo para a fonte e o nível de interesse.',
    ],
    correct: 2,
    explanation: 'Horário, nível e provedor permitem acompanhar o comportamento daquela fonte. Uma contagem total perde a distribuição no tempo.',
  },
  {
    slide: 3,
    question: 'Onde um evento atravessa a fronteira entre o Windows e o Docker nesta arquitetura?',
    choices: [
      'No JSONL que o PowerShell grava e o Logstash lê por montagem.',
      'No índice que o Kibana transfere ao Logstash.',
      'Na API local que o Windows usa para registrar o evento no canal Aplicativo.',
    ],
    correct: 0,
    explanation: 'O PowerShell roda no Windows. A pasta do JSONL é montada no container para o Logstash ler.',
  },
  {
    slide: 4,
    question: 'O coletor ficou parado e o Windows registrou eventos. Como o script retoma?',
    choices: [
      'Pede ao Kibana para buscar a hora da última atualização.',
      'Lê o sincedb para localizar a próxima entrada no canal.',
      'Procura RecordIds acima do checkpoint, para registros ainda retidos.',
    ],
    correct: 2,
    explanation: 'O checkpoint guarda a posição da coleta no canal Aplicativo. O sincedb cuida da leitura do arquivo em outro estágio.',
  },
  {
    slide: 5,
    question: 'O Logstash relê um trecho do JSONL. O que evita duplicatas no índice?',
    choices: [
      'O codec json verifica a unicidade antes de decodificar.',
      'A saída usa o event.id estável como document_id no mesmo índice.',
      'O filtro mutate exclui eventos cujo horário já apareceu.',
    ],
    correct: 1,
    explanation: 'O mesmo ID aponta para o mesmo documento. O sincedb diminui releituras, e a escrita com ID estável mantém o índice consistente se elas ocorrerem.',
  },
  {
    slide: 6,
    question: 'Que tipo de campo serve para agrupar pelos valores exatos de event.code?',
    choices: [
      'keyword, pois o código é uma categoria.',
      'date, pois o código identifica uma ocorrência no tempo.',
      'long, pois o objetivo é somar os códigos dos eventos.',
    ],
    correct: 0,
    explanation: 'Um código numérico na aparência pode funcionar como rótulo. O mapeamento define event.code como keyword para busca e agrupamento exatos.',
  },
  {
    slide: 7,
    question: 'Quem calcula a contagem por provedor que o Kibana apresenta?',
    choices: [
      'O navegador, a partir de todas as linhas do JSONL.',
      'O Logstash, a cada vez que o dashboard atualiza.',
      'O Elasticsearch, por uma agregação solicitada pelo Kibana.',
    ],
    correct: 2,
    explanation: 'Kibana envia a consulta e exibe o retorno. Elasticsearch pesquisa os documentos e executa a agregação.',
  },
  {
    slide: 8,
    question: 'Você quer ver apenas erros e montar um gráfico por ID. Qual caminho usar?',
    choices: [
      'Selecionar a busca por código no dashboard e executar a contagem dentro da KQL.',
      'Selecionar o Data View, filtrar no Discover e abrir event.code com Visualize no Lens.',
      'Alterar o campo de tempo do Data View para event.code e ler o histograma.',
    ],
    correct: 1,
    explanation: 'KQL recorta os documentos, e Visualize abre o editor de gráficos do Lens. No roteiro, limpe a consulta antes do Lens para ver os códigos do recorte geral.',
  },
  {
    slide: 9,
    question: 'Que tarefa pode ser feita pela interface durante a demonstração?',
    choices: [
      'Configurar a coleta por RecordId no Windows.',
      'Definir a remoção de campos técnicos no Logstash.',
      'Montar um gráfico por ID no Lens e aplicar filtro por clique.',
    ],
    correct: 2,
    explanation: 'A interface cobre visualização e exploração. A coleta e o processamento usam o script e o arquivo de configuração do projeto.',
  },
  {
    slide: 10,
    question: 'Que medida faz sentido ao adaptar a ideia para produção?',
    choices: [
      'Manter a segurança desligada e ampliar o intervalo de atualização.',
      'Configurar autenticação e TLS e dimensionar os serviços para a carga.',
      'Expor as portas locais e manter o heap de demonstração como referência de capacidade.',
    ],
    correct: 1,
    explanation: 'Os parâmetros da demo foram escolhidos para um computador e um volume pequeno. Em produção, segurança, capacidade e manutenção entram no desenho.',
  },
  {
    slide: 11,
    question: 'O endpoint _count mostra um total maior que o dashboard. O que conferir primeiro?',
    choices: [
      'Se Last 7 days ou os filtros excluem parte dos documentos do índice.',
      'Se o Kibana ainda precisa armazenar os eventos que o Elasticsearch retornou.',
      'Se o Visualizador de Eventos está com o painel de mensagens fechado.',
    ],
    correct: 0,
    explanation: 'O endpoint sem filtro abrange o índice inteiro. O dashboard calcula o total no período e nos filtros selecionados.',
  },
  {
    slide: 12,
    question: 'O gráfico revela um pico em uma fonte. Como responder se já encontramos a causa?',
    choices: [
      'Sim, porque toda categoria mais frequente é a causa do incidente.',
      'Sim, se a barra puder ser filtrada por clique.',
      'O pico orienta a investigação. É preciso cruzar outras evidências para confirmar a causa.',
    ],
    correct: 2,
    explanation: 'O gráfico ajuda a localizar quando e onde investigar. Um agrupamento sozinho não estabelece causalidade.',
  },
]

export const glossary = [
  { term: 'Agregação', definition: 'Operação que resume documentos em métricas ou grupos. O gráfico por nível conta os eventos em cada categoria de log.level.' },
  { term: 'API REST', definition: 'Interface HTTP para consultar e operar um serviço. Na demo, GET /windows-events/_count devolve a quantidade de documentos no índice.' },
  { term: '@timestamp', definition: 'Campo de data e hora do evento, exportado em UTC. O Data View o usa para restringir a busca no tempo, com exibição no fuso configurado no Kibana.' },
  { term: 'Campo', definition: 'Atributo de um documento. log.level guarda o nível e event.provider identifica a fonte do evento.' },
  { term: 'Checkpoint', definition: 'Estado do coletor PowerShell com o último RecordId exportado do canal Aplicativo.' },
  { term: 'Dashboard', definition: 'Conjunto de painéis que podem compartilhar intervalo e filtros. A demo tem quatro visualizações originais em Eventos do Windows.' },
  { term: 'Data View', definition: 'Configuração do Kibana para localizar os dados e selecionar o campo de tempo. Eventos do Windows usa windows-events e @timestamp.' },
  { term: 'Discover', definition: 'Área do Kibana para examinar documentos, histograma e campos de um recorte de dados.' },
  { term: 'Docker', definition: 'Ambiente de containers. O Compose reúne Elasticsearch, Logstash e Kibana, enquanto o coletor roda no Windows.' },
  { term: 'document_id', definition: 'Identificador que o Logstash informa ao Elasticsearch na escrita. A demo usa event.id para que uma releitura atualize o mesmo documento.' },
  { term: 'Documento', definition: 'Registro JSON indexado no Elasticsearch. Cada evento coletado corresponde a um documento identificado.' },
  { term: 'Elasticsearch', definition: 'Componente que armazena, indexa, pesquisa e agrega os documentos.' },
  { term: 'ELK Stack', definition: 'Nome formado por Elasticsearch, Logstash e Kibana. Elastic Stack é um ecossistema mais amplo, com ferramentas adicionais.' },
  { term: 'Event Log', definition: 'Sistema de registro de eventos do Windows. A demonstração lê o canal Application, chamado Aplicativo na interface em português.' },
  { term: 'filter', definition: 'Estágio do Logstash que modifica um evento. O mutate da demo remove campos técnicos.' },
  { term: 'Índice', definition: 'Conjunto de documentos pesquisáveis no Elasticsearch. A demonstração escreve em windows-events.' },
  { term: 'input', definition: 'Estágio de entrada do Logstash. file acompanha o JSONL, com codec json para decodificar cada linha.' },
  { term: 'JSON', definition: 'Formato de texto que representa objetos, listas e valores. Os documentos de evento têm campos estruturados em JSON.' },
  { term: 'JSONL', definition: 'JSON Lines. Cada linha é um objeto JSON completo. O coletor acrescenta um evento por linha em eventos.jsonl.' },
  { term: 'Kibana', definition: 'Interface web para formular consultas e visualizar resultados do Elasticsearch, incluindo documentos, gráficos e dashboards.' },
  { term: 'KQL', definition: 'Kibana Query Language, usada para filtrar documentos. log.level : "Error" seleciona eventos com nível Error.' },
  { term: 'Lens', definition: 'Editor visual do Kibana para montar gráficos e outras visualizações a partir dos campos disponíveis.' },
  { term: 'Logstash', definition: 'Processador de ingestão com entrada, filtros e saídas. A demo usa o arquivo como entrada e o Elasticsearch como saída.' },
  { term: 'Mapeamento', definition: 'Definição dos tipos dos campos de um índice. A demo usa date, keyword e long no template do projeto.' },
  { term: 'output', definition: 'Estágio de saída do Logstash. A saída elasticsearch grava o evento em windows-events.' },
  { term: 'Pipeline', definition: 'Sequência de etapas que conduz os dados. No Logstash, a configuração divide a sequência em input, filter e output.' },
  { term: 'RecordId', definition: 'Número de registro no canal do Windows. O coletor o usa como referência de progresso.' },
  { term: 'sincedb', definition: 'Estado do plugin file do Logstash com a posição de leitura do arquivo. Permite retomar a ingestão de linhas.' },
]
