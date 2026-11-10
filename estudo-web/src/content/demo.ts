export const startCommand = 'powershell -ExecutionPolicy Bypass -File .\\iniciar.ps1'
const pauseCollector = 'powershell -ExecutionPolicy Bypass -File .\\scripts\\parar_demo.ps1 -SomenteColetor'
export const restoreDashboard = startCommand + ' -RestaurarDashboard'
const composeStatus = 'docker compose ps'
const logstashLogs = 'docker compose logs --tail 50 logstash'
const dockerMemory = 'docker stats --no-stream'
const collectorTail = 'Get-Content .\\runtime\\state\\coletor.log -Tail 3'
const jsonlTail = 'Get-Content .\\runtime\\logs\\eventos.jsonl -Tail 1'
export const errorQuery = 'log.level : "Error"'
export const countUrl = 'http://localhost:9200/windows-events/_count'
export const kibanaUrl = 'http://localhost:5601'
export const dashboardUrl = kibanaUrl + '/app/dashboards#/view/eventos-windows'

export type PrepItem = {
  id: string
  title: string
  action: string
  commands?: readonly string[]
}

export const preparation: PrepItem[] = [
  {
    id: 'docker',
    title: 'Conferir Docker e memória',
    action: 'Abra o Docker Desktop e espere Engine running. Confira cerca de 3 GB de RAM disponíveis no Windows com o Docker aberto. Ajuste a preparação com antecedência se a máquina estiver lenta.',
    commands: [dockerMemory],
  },
  {
    id: 'start',
    title: 'Subir o ambiente e validar a chegada',
    action: 'Na raiz, rode o comando oficial. O atalho chama scripts/iniciar_demo.ps1. Confira as seis etapas, Elasticsearch e Kibana healthy, Logstash em execução e a contagem do índice. Abra o dashboard em Last 7 days e confira os quatro painéis.',
    commands: [startCommand, composeStatus, countUrl],
  },
  {
    id: 'screens',
    title: 'Organizar as telas',
    action: 'Deixe aberto o Visualizador em Logs do Windows → Aplicativo. Em Exibir, oculte o painel de visualização da mensagem. Prepare PowerShell na raiz, o pipeline no editor e a Home do Kibana. O roteiro sugere zoom de 125% no navegador. Se aparecer Your data is not secure, o roteiro usa Don’t show again → Dismiss.',
    commands: ['eventvwr.msc', 'logstash/pipeline/windows-events.conf'],
  },
  {
    id: 'contingency',
    title: 'Ensaiar e preparar a contingência',
    action: 'Cronometre o percurso inteiro. Se preparar um vídeo, grave o ensaio com as mensagens ocultas e teste a reprodução local. Se tiver salvo o gráfico extra do Lens, restaure os quatro painéis originais antes da apresentação.',
    commands: [restoreDashboard],
  },
  {
    id: 'pause',
    title: 'Pausar somente o coletor',
    action: 'Com a stack pronta, pare só a coleta. Windows continua registrando e os containers continuam no ar. Eventos que surgirem no canal e forem retidos durante a pausa ficam depois do checkpoint e podem aparecer na retomada. A pausa por si só não gera eventos.',
    commands: [pauseCollector],
  },
]

type DemoStep = {
  id: string
  at: string
  title: string
  goal: string
  path: string
  cue: string
  commands?: readonly string[]
  link?: { title: string; url: string }
  note?: string
}

export const demoSteps: DemoStep[] = [
  {
    id: 'event-viewer',
    at: '00:00',
    title: 'Mostrar a origem no Windows',
    goal: 'Identificar a fonte dos dados e os metadados.',
    path: 'Visualizador de Eventos → Logs do Windows → Aplicativo. Em Exibir, mantenha o painel de mensagens oculto. Aponte horário, nível, fonte e ID.',
    cue: 'Esta é a fonte dos eventos. Vamos aproveitar campos como horário, nível, fonte e ID.',
    commands: ['eventvwr.msc'],
  },
  {
    id: 'collector',
    at: '00:40',
    title: 'Retomar o coletor PowerShell',
    goal: 'Mostrar como a coleta continua de onde parou.',
    path: 'No PowerShell, na raiz do repositório, execute o atalho. Ele confere os serviços e retoma a leitura pelo checkpoint.',
    cue: 'Os serviços já estão prontos. O script retoma a coleta e o Windows será consultado a cada quinze segundos.',
    commands: [startCommand],
  },
  {
    id: 'jsonl',
    at: '01:10',
    title: 'Conferir o log e uma linha do JSONL',
    goal: 'Ligar um registro da origem ao arquivo que a ingestão lê.',
    path: 'Leia o fim do log do coletor e a última linha do arquivo. Aponte horário, nível e código. Se nada novo chegou, mostre a última linha já coletada.',
    cue: 'O checkpoint orienta a retomada. Quando chegam novos registros, cada evento acrescenta uma linha JSON.',
    commands: [collectorTail, jsonlTail],
  },
  {
    id: 'logstash',
    at: '01:50',
    title: 'Percorrer o pipeline do Logstash',
    goal: 'Explicar como uma linha se torna um documento pesquisável.',
    path: 'No editor, abra windows-events.conf. Aponte input file com codec json, filter mutate e output elasticsearch com document_id.',
    cue: 'A entrada lê, o filtro remove campos técnicos e a saída grava com um ID estável. Se a linha for relida, o mesmo documento é atualizado.',
    commands: ['logstash/pipeline/windows-events.conf'],
    note: 'O sincedb guarda a posição no arquivo. O checkpoint guarda o RecordId no canal Aplicativo.',
  },
  {
    id: 'count',
    at: '02:20',
    title: 'Abrir a contagem do Elasticsearch',
    goal: 'Confirmar que o índice windows-events recebeu documentos.',
    path: 'No navegador da apresentação, abra a API local e aponte o campo count.',
    cue: 'Este é o total do índice. O dashboard pode mostrar um recorte menor porque tem período e filtros.',
    link: { title: 'Abrir contagem local', url: countUrl },
    commands: [countUrl],
  },
  {
    id: 'discover',
    at: '02:40',
    title: 'Explorar e filtrar no Discover',
    goal: 'Responder quais erros apareceram na última semana.',
    path: 'Menu → Analytics → Discover. Em Data view, escolha Eventos do Windows. Selecione Last 7 days. Às 03:10, digite a KQL e pressione Enter. Confira o histograma e os documentos e limpe a consulta para seguir.',
    cue: 'Aqui estão os documentos dentro do período. A KQL deixa na lista apenas os eventos do nível Error.',
    link: { title: 'Abrir Kibana local', url: kibanaUrl },
    commands: [errorQuery],
  },
  {
    id: 'lens',
    at: '03:40',
    title: 'Montar o gráfico no Lens',
    goal: 'Transformar event.code numa visualização por ID.',
    path: 'No Discover, com a consulta limpa, abra a prévia de event.code e escolha Visualize. Mostre a sugestão do Lens e a contagem por código.',
    cue: 'A partir deste campo, o Lens já sugere um gráfico. Podemos comparar os códigos mais frequentes.',
  },
  {
    id: 'dashboard',
    at: '04:30',
    title: 'Filtrar os painéis com um clique',
    goal: 'Mostrar como um filtro muda a leitura do dashboard inteiro.',
    path: 'Em Eventos do Windows, use Last 7 days. Aponte total, nível, provedor e evolução no tempo. Clique numa barra de Eventos por nível, confira log.level e remova o filtro no ×. Pelo menu do gráfico, a ação equivalente é Filter for.',
    cue: 'Um clique recorta todos os painéis. A tela refaz a consulta a cada trinta segundos.',
    link: { title: 'Abrir dashboard local', url: dashboardUrl },
    note: 'Às 05:00, volte aos slides e passe a conclusão para Yahn. Os valores da captura são históricos.',
  },
]

export const troubleshooting = [
  {
    title: 'Não chegaram eventos novos',
    action: 'Confira a última linha do log. Mostre registros já coletados e explique a verificação a cada 15 s. Eventos novos dependem do que o Windows registrar.',
    command: collectorTail,
  },
  {
    title: 'O filtro Error ficou vazio',
    action: 'Confira Last 7 days e o Data View. Se houver avisos no período, use Warning para mostrar o mesmo mecanismo. Depois limpe a consulta.',
    command: 'log.level : "Warning"',
  },
  {
    title: 'Kibana ainda está carregando',
    action: 'Na preparação, aguarde até quatro minutos e confira se Elasticsearch e Kibana estão healthy. Use a contingência se o atraso consumir o tempo da apresentação.',
    command: composeStatus,
  },
  {
    title: 'Logstash está atrasado',
    action: 'Confira se existe JSONL e se o pipeline main iniciou. Aguarde a leitura. Compare IDs únicos do arquivo com a contagem, pois o arquivo pode ter linhas repetidas.',
    command: logstashLogs,
  },
  {
    title: 'A memória está insuficiente',
    action: 'Confira a memória do Windows e o consumo dos containers. Se o computador continuar sem folga para a stack, use a contingência gravada no ensaio.',
    command: dockerMemory,
  },
]
