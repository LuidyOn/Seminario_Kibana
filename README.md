# Kibana na prática: eventos reais do Windows com Logstash e Elasticsearch

Demonstração didática do **Kibana** para o seminário técnico da disciplina **Projeto de Desenvolvimento de Dashboard Analítico** (Avaliação de Produto 2): apresentação de 7 a 20 minutos com slides e demonstração prática da ferramenta.

> **Ambiente local didático para demonstração e desenvolvimento, não destinado à produção.**

## Objetivo

Mostrar, com **eventos reais do Windows do próprio computador**, como os dados são coletados automaticamente, processados pelo **Logstash**, armazenados no **Elasticsearch** e analisados no **Kibana**: Discover, filtros KQL, Lens e Dashboard.

## Guia interativo de estudos

O site em [estudo-web/](estudo-web/) reúne os 12 slides, as falas de Luiz e Yahn, o cronômetro de ensaio, o roteiro prático e os exercícios de revisão. O progresso fica no navegador. O site funciona com a stack desligada.

### Abrir no computador

Com Node.js 24, execute na raiz do repositório:

```powershell
cd estudo-web
npm.cmd ci
npm.cmd run dev
```

Abra [http://localhost:5173](http://localhost:5173). Para gerar os arquivos estáticos em `estudo-web/dist/`, rode `npm.cmd run build` na pasta do site. Confira o build com `npm.cmd run preview` em [http://localhost:4173](http://localhost:4173).

### Publicar no GitHub Pages

1. Faça o push do commit para `main` com `git push origin main`.
2. No repositório do GitHub, abra **Settings → Pages → Build and deployment → Source** e selecione **GitHub Actions**.
3. Abra **Actions → Publicar guia de estudos → Run workflow**. Selecione `main` e clique em **Run workflow**.
4. Após o job **deploy** concluir, volte a **Settings → Pages → Visit site** e copie a URL mostrada pelo GitHub. O endereço padrão de um projeto é `https://<usuario>.github.io/<repositorio>/`.

O [workflow](.github/workflows/estudo-pages.yml) publica somente o build de `estudo-web/dist/`. Se o plano ou as configurações impedirem o Pages público, gere o build local e publique somente o conteúdo de `dist/` em uma hospedagem estática ou em um repositório público separado habilitado para Pages. Os links do roteiro para as portas 5601 e 9200 funcionam na máquina em que a stack roda.

## Demonstração prática — Guia rápido (5 minutos)

1. **Visualizador de Eventos**

   ```powershell
   eventvwr.msc
   ```

   **Logs do Windows → Aplicativo**. Em **Exibir**, oculte o painel de visualização.
   “Esta lista é a fonte dos eventos. A coleta usa apenas os metadados de cada registro.”

2. **Coletor PowerShell**

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\iniciar.ps1
   ```

   “O script confere os serviços e inicia ou retoma a coleta a cada 15 segundos.”

3. **Arquivo `eventos.jsonl`**

   ```powershell
   Get-Content .\runtime\state\coletor.log -Tail 3
   Get-Content .\runtime\logs\eventos.jsonl -Tail 1
   ```

   “O coletor registra cada evento em uma linha JSON e guarda de onde deve retomar.”

4. **Pipeline do Logstash**

   Abra [windows-events.conf](logstash/pipeline/windows-events.conf) no editor.
   “A entrada lê o JSON, o filtro remove campos técnicos e a saída envia o evento ao Elasticsearch com um ID estável.”

5. **Elasticsearch**

   Abra a [contagem do índice](http://localhost:9200/windows-events/_count).

   ```text
   http://localhost:9200/windows-events/_count
   ```

   “O campo `count` mostra quantos eventos o Elasticsearch já indexou.”

6. **Discover e KQL**

   No [Kibana](http://localhost:5601), abra **Menu → Analytics → Discover**. No seletor **Data view**, escolha **Eventos do Windows** e use **Last 7 days**. Digite o filtro e pressione **Enter**.

   ```text
   http://localhost:5601
   ```

   ```kql
   log.level : "Error"
   ```

   “A KQL reduz a lista aos eventos do nível selecionado.”

7. **Lens**

   Limpe a consulta. Abra a prévia do campo `event.code` e escolha **Visualize → Save**. Use o título `IDs de evento mais frequentes`, escolha **Existing → Eventos do Windows → Save and go to dashboard** e salve o dashboard com **Save**. Saia do modo de edição com **Exit edit**, se necessário.
   “O Lens sugere um gráfico a partir de um campo. Podemos incluí-lo no dashboard.”

8. **Dashboard interativo**

   No [dashboard Eventos do Windows](http://localhost:5601/app/dashboards#/view/eventos-windows), clique em uma barra de **Eventos por nível**. Confira o filtro `log.level` e remova-o no **×**.

   ```text
   http://localhost:5601/app/dashboards#/view/eventos-windows
   ```

   “Um clique aplica o mesmo filtro a todos os painéis.”

Na raiz do repositório, use estes comandos para iniciar, encerrar com os dados preservados e restaurar os quatro painéis originais depois de um ensaio, respectivamente.

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\parar_demo.ps1
powershell -ExecutionPolicy Bypass -File .\iniciar.ps1 -RestaurarDashboard
```

O [roteiro detalhado](docs/roteiro_demonstracao.md) inclui a preparação, o diagnóstico e o plano de contingência.

## Arquitetura

```text
Windows Event Log (canal Application)
      │  Get-WinEvent, a cada 15 s (scripts/coletar_eventos.ps1, roda no Windows)
      ▼
runtime/logs/eventos.jsonl   ← um JSON por linha; só neste computador, fora do Git
      │  leitura contínua do arquivo
      ▼
Logstash 9.5.5 ── entrada file + codec json → filtro → saída elasticsearch
      ▼
Elasticsearch 9.5.5 ── índice windows-events                            porta 9200
      ▼
Kibana 9.5.5 ── Data View → Discover · Lens · Dashboard "Eventos do Windows"   porta 5601
```

Logstash, Elasticsearch e Kibana rodam em containers definidos em [docker-compose.yml](docker-compose.yml), na mesma versão (exigência da Elastic). Elasticsearch e Kibana aceitam conexões apenas da própria máquina (`127.0.0.1`); o Logstash não expõe portas.

| Caminho | Finalidade |
|---|---|
| `docker-compose.yml` | Sobe Elasticsearch, Logstash e Kibana (nó único, ambiente local) |
| `iniciar.ps1` | Atalho na raiz para o script de início |
| `scripts/iniciar_demo.ps1` | Um comando para subir tudo: containers, coletor e dashboard |
| `scripts/parar_demo.ps1` | Para o coletor e os containers, preservando os dados |
| `scripts/coletar_eventos.ps1` | Coletor: lê o canal Application e grava `runtime/logs/eventos.jsonl` |
| `logstash/pipeline/windows-events.conf` | Pipeline do Logstash (entrada, filtro e saída) |
| `logstash/windows-events-template.json` | Tipos dos campos do índice `windows-events` |
| `kibana/dashboard_eventos.ndjson` | Objetos do Kibana: Data View, 4 visualizações e o dashboard |
| `docs/` | Conteúdo do seminário, roteiros e referências |
| `slides/` | Apresentação (`.pptx`) e o script que a gera |
| `runtime/` | Criada na primeira execução: eventos coletados e estado da coleta (**ignorada pelo Git**) |

## O que é coletado

- **Coletado:** horário do evento (UTC), canal (`Application`), provedor (fonte), ID do evento, `RecordId`, nível normalizado (`Critical`, `Error`, `Warning`, `Information` ou `Verbose`) e um identificador aleatório desta instalação.
- **Não coletado:** a mensagem do evento, usuário, nome do computador, processos e os dados internos do evento. O canal de Segurança não é lido.
- Os eventos e o estado da coleta ficam em `runtime/`, que o Git ignora. Cada computador coleta os próprios eventos.

## Pré-requisitos

- Windows 10 ou 11 com Windows PowerShell 5.1 (já incluso no sistema);
- Docker Desktop com Docker Compose v2;
- cerca de 3 GB de RAM disponíveis no Windows com o Docker Desktop já aberto. O consumo dos containers varia durante a inicialização e as consultas;
- espaço em disco para as imagens (só as do Elasticsearch e do Kibana somam cerca de 5 GB) e internet na primeira execução, para baixá-las;
- navegador atualizado (Chrome, Edge ou Firefox).

## Como executar

Na pasta do projeto, num terminal PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar.ps1
```

O atalho delega a `scripts/iniciar_demo.ps1`. A opção `-ExecutionPolicy Bypass` vale para esse processo do PowerShell. O script:

1. confere o Docker (e tenta iniciar o Docker Desktop, se estiver fechado) e avisa se houver pouca RAM livre;
2. cria a pasta `runtime\`;
3. sobe os containers e espera ficarem prontos (`docker compose up -d --wait`);
4. inicia o coletor em segundo plano, sem nunca abrir um segundo coletor;
5. importa o dashboard no Kibana, se ainda não existir;
6. confere se os eventos estão chegando ao índice `windows-events`.

Depois, abra o [dashboard Eventos do Windows](http://localhost:5601/app/dashboards#/view/eventos-windows). Se o Kibana exibir a tela de boas-vindas, selecione **Explore on my own**.

Você pode executar o comando de novo para retomar a demonstração com o mesmo coletor e os mesmos dados. Com `-RestaurarDashboard`, o dashboard volta aos quatro painéis originais do repositório.

## Verificar

```powershell
docker compose ps                                      # elasticsearch e kibana "healthy"; logstash em execução
curl.exe http://localhost:9200/windows-events/_count   # quantidade de eventos no índice
Get-Content runtime\state\coletor.log -Tail 10         # atividade do coletor
```

## Parar

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\parar_demo.ps1
```

Para o coletor (por sinal, com checkpoint salvo) e os containers (`docker compose stop`). Nada é apagado: o índice, o dashboard e a pasta `runtime\` continuam disponíveis para a próxima execução. Com `-SomenteColetor`, os containers continuam no ar.

## Como a coleta funciona

- **Primeira execução:** importa os eventos dos últimos 7 dias, até 2.000.
- **Depois:** a cada 15 s, lê só os eventos com `RecordId` maior que o último exportado. O checkpoint fica em `runtime\state\checkpoint.json`. Novos eventos aparecem no Kibana após esse intervalo mais o tempo de leitura do Logstash; não é instantâneo.
- **Instância única:** um segundo coletor da mesma cópia do projeto se recusa a iniciar.
- **Sem duplicação no índice:** cada evento recebe um ID estável (`Application-<RecordId>-<horário>`), usado pelo Logstash como `document_id`. Se o arquivo for relido (por exemplo, se o Logstash perder a posição de leitura após reiniciar), os documentos são sobrescritos, não duplicados. Após uma falha, o arquivo pode conter linhas repetidas; o índice, não.
- **Avisos:** se o log do Windows for limpo, ou se eventos forem descartados pelo log circular antes da coleta, o coletor registra isso em `runtime\state\coletor.log`.
- O coletor só funciona enquanto o projeto está ativo; não há serviço nem tarefa agendada.

## Levar para outro computador

1. Clonar o repositório. A pasta `runtime/` fica na máquina que coletou os eventos.
2. Abrir o Docker Desktop e executar `powershell -ExecutionPolicy Bypass -File .\iniciar.ps1` na raiz.
3. O coletor cria `runtime\` e coleta os eventos **daquele** computador; o dashboard é importado automaticamente.

## Validação

- **Testado no computador de desenvolvimento (29/10/2026):** o coletor leu 1.891 eventos reais dos últimos 7 dias e gerou JSON Lines válido, só com os campos permitidos; uma amostra conferiu com o `Get-WinEvent`; a coleta incremental, a instância única, a parada por sinal, a retomada pelo checkpoint e os avisos de log limpo e de lacuna funcionaram; uma cópia em outra pasta criou o próprio `runtime/`.
- **Retomada no computador da apresentação (09/11/2026):** o coletor retomou pelo checkpoint, o Logstash com heap de 256 MB enviou os eventos ao índice `windows-events` e o Kibana preservou os seis objetos salvos. O atalho `iniciar.ps1` foi testado no PowerShell 5.1 com a stack ativa e reutilizou o coletor. Discover, KQL, Lens e os quatro painéis do dashboard foram conferidos no Kibana 9.5.5.

## Limitações do ambiente didático

- **Segurança desabilitada** (`xpack.security.enabled=false`): sem login e sem TLS, para simplificar a demonstração. É uma simplificação didática, nunca uma recomendação de produção; o próprio Kibana exibe o aviso *Your data is not secure*.
- **Nó único e memória reduzida:** Elasticsearch com 512 MB de heap e Logstash com 256 MB, abaixo da recomendação da Elastic para ingestão típica (4 a 8 GB). Adequado ao volume pequeno da demo, não a produção.
- **Coleta periódica e restrita:** verificação a cada 15 s, só o canal Application e só metadados.
- **Pasta compartilhada com o Docker:** a documentação do Logstash alerta que o controle de leitura (*sincedb*) pode não se manter em sistemas de arquivos remotos; por isso o ID estável evita duplicação se o arquivo for relido.
- **Somente Windows:** o coletor usa `Get-WinEvent`.

## Documentação

- [docs/conteudo_seminario.md](docs/conteudo_seminario.md): conteúdo teórico do seminário
- [docs/roteiro_apresentacao.md](docs/roteiro_apresentacao.md): roteiro da fala (≈ 16 min)
- [docs/roteiro_demonstracao.md](docs/roteiro_demonstracao.md): validação inicial, demonstração, diagnóstico e contingência
- [docs/referencias.md](docs/referencias.md): fontes consultadas

Os [slides editáveis](slides/seminario_kibana.pptx) são gerados por `slides/gerar_slides.py`. Para regenerar no Windows, instale a dependência com `py -3 -m pip install python-pptx` e execute `py -3 .\slides\gerar_slides.py`. Os caminhos e enquadramentos das capturas estão em [slides/assets](slides/assets/README.md).
