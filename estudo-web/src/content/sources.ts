export const projectSources = [
  { path: 'slides/seminario_kibana.pptx', use: 'Títulos, sequência, notas de fala e enquadramento das capturas.' },
  { path: 'docs/roteiro_apresentacao.md', use: 'Tempos estimados e ligações entre os assuntos.' },
  { path: 'docs/conteudo_seminario.md', use: 'Explicações sobre arquitetura, coleta, ingestão e exploração.' },
  { path: 'README.md · docs/roteiro_demonstracao.md', use: 'Comandos, preparação, navegação no Kibana e contingência.' },
  { path: 'scripts/ · logstash/ · docker-compose.yml', use: 'Conferência do comportamento do coletor, do pipeline, dos tipos e das portas.' },
  { path: 'docs/referencias.md', use: 'Bibliografia completa e datas de consulta do seminário.' },
]

export const officialSources = [
  { label: 'Elastic Stack', url: 'https://www.elastic.co/docs/get-started/the-stack' },
  { label: 'Índices e documentos', url: 'https://www.elastic.co/docs/manage-data/data-store/index-basics' },
  { label: 'Data Views', url: 'https://www.elastic.co/docs/explore-analyze/find-and-organize/data-views' },
  { label: 'Discover', url: 'https://www.elastic.co/docs/explore-analyze/discover' },
  { label: 'KQL', url: 'https://www.elastic.co/docs/explore-analyze/query-filter/languages/kql' },
  { label: 'Lens', url: 'https://www.elastic.co/docs/explore-analyze/visualize/lens' },
  { label: 'Dashboards', url: 'https://www.elastic.co/docs/explore-analyze/dashboards' },
  { label: 'Objetos salvos', url: 'https://www.elastic.co/docs/explore-analyze/find-and-organize/saved-objects' },
  { label: 'Funcionamento do Logstash', url: 'https://www.elastic.co/docs/reference/logstash/how-logstash-works' },
  { label: 'Entrada file e sincedb', url: 'https://www.elastic.co/docs/reference/logstash/plugins/plugins-inputs-file' },
  { label: 'Saída Elasticsearch e document_id', url: 'https://www.elastic.co/docs/reference/logstash/plugins-outputs-elasticsearch' },
  { label: 'Get-WinEvent', url: 'https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent' },
  { label: 'Segurança do Elasticsearch', url: 'https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/security-settings' },
  { label: 'Licenças da Elastic', url: 'https://www.elastic.co/subscriptions' },
]
