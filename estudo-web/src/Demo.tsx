import {
  dashboardUrl, demoSteps, kibanaUrl, preparation, restoreDashboard, troubleshooting,
} from './content/demo'
import type { Progress } from './progress'
import type { DemoPage } from './route'
import { slideLink } from './route'
import { Check, Command, Detail, Meter, Stopwatch, twoDigits } from './ui'

export function Demo({ view, progress }: { view: DemoPage; progress: Progress }) {
  const isPrep = view === 'preparacao'
  const ready = preparation.filter(({ id }) => progress.checked('prep-' + id)).length
  const practiced = demoSteps.filter(({ id }) => progress.checked('demo-' + id)).length

  return (
    <div className="demo">
      <header className="page-intro demo-intro">
        <div>
          <p className="eyebrow red">Slide 11 <span /> Luiz Oliveira</p>
          <h1>Demonstração prática</h1>
          <p>Do canal Aplicativo ao filtro por clique no dashboard, em uma única execução.</p>
        </div>
        <a className="text-link" href={slideLink(11, 'luiz')}>Estudar slide 11 <span aria-hidden="true">→</span></a>
      </header>
      <nav className="page-tabs" aria-label="Visões da demonstração">
        <a href="#/demo/preparacao" aria-current={isPrep ? 'page' : undefined}>
          Preparação prévia <small>{ready}/{preparation.length}</small>
        </a>
        <a href="#/demo/roteiro" aria-current={!isPrep ? 'page' : undefined}>
          Roteiro rápido <small>5 min</small>
        </a>
      </nav>
      <div className="local-note">
        <span className="local-dot" aria-hidden="true" />
        <p>As portas <code>localhost:5601</code> e <code>localhost:9200</code> só funcionam no computador que estiver rodando a stack.</p>
      </div>
      {isPrep ? (
        <section className="demo-prep" aria-labelledby="prep-title">
          <header className="section-heading">
            <div><h2 id="prep-title">Antes de apresentar</h2><p>Conclua esta lista antes de iniciar o cronômetro.</p></div>
            <span className="time-chip">{ready}/{preparation.length} prontos</span>
          </header>
          <ol className="prep-list">
            {preparation.map(({ id, title, action, commands }, index) => (
              <li className="surface prep-item" key={id}>
                <span className="card-number" aria-hidden="true">{twoDigits(index + 1)}</span>
                <div>
                  <h3>{title}</h3>
                  <p>{action}</p>
                  {commands?.map((command) => <Command key={command} value={command} />)}
                  {id === 'start' && <a className="text-link" href={dashboardUrl} target="_blank" rel="noreferrer">Conferir dashboard local <span aria-hidden="true">↗</span></a>}
                  {id === 'screens' && <a className="text-link" href={kibanaUrl} target="_blank" rel="noreferrer">Abrir Kibana local <span aria-hidden="true">↗</span></a>}
                  <Check progress={progress} id={'prep-' + id}>Concluí este preparo <span className="sr-only">· {title}</span></Check>
                </div>
              </li>
            ))}
          </ol>
          <a className="button button-primary" href="#/demo/roteiro">Ir para o roteiro rápido <span aria-hidden="true">→</span></a>
        </section>
      ) : (
        <section aria-labelledby="run-title" className="demo-run">
          <div className="demo-overview">
            <div className="surface demo-track">
              <h2 id="run-title">Roteiro rápido · 5 minutos</h2>
              <p>{practiced}/{demoSteps.length} etapas praticadas</p>
              <Meter value={practiced} max={demoSteps.length} label="Etapas praticadas" tone="red" />
            </div>
            <Stopwatch target={300} />
          </div>
          <dl className="cadence">
            <div><dt>15 s</dt><dd>PowerShell verifica o Windows</dd></div>
            <div><dt>Contínuo</dt><dd>Logstash acompanha o JSONL</dd></div>
            <div><dt>30 s</dt><dd>Dashboard refaz a consulta</dd></div>
          </dl>
          <ol className="demo-steps">
            {demoSteps.map((step, index) => (
              <li key={step.id} className="surface demo-step">
                <div className="step-meta"><span className="card-number" aria-hidden="true">{twoDigits(index + 1)}</span><span className="time-chip">{step.at}</span></div>
                <div className="step-body">
                  <h3>{step.title}</h3>
                  <p className="step-goal">{step.goal}</p>
                  <p>{step.path}</p>
                  {step.commands?.map((value) => <Command key={value} value={value} />)}
                  {step.id === 'lens' && (
                    <>
                      <Command value="event.code" />
                      <Detail title="Salvar o gráfico no dashboard">
                        <p>O roteiro completo inclui <strong>Save</strong> → <strong>Title</strong> <code>IDs de evento mais frequentes</code> → <strong>Existing</strong> → <strong>Eventos do Windows</strong> → <strong>Save and go to dashboard</strong> → <strong>Save</strong>. Use <strong>Exit edit</strong> se necessário.</p>
                        <p>Se estiver com pouco tempo, mostre a prévia e abra o dashboard original. Salvar acrescenta um painel. Se o fizer no ensaio, restaure os quatro originais antes da apresentação.</p>
                        <Command value={restoreDashboard} />
                      </Detail>
                    </>
                  )}
                  {step.id === 'dashboard' && <Command value={dashboardUrl} />}
                  {step.link && <a className="text-link" href={step.link.url} target="_blank" rel="noreferrer">{step.link.title} <span aria-hidden="true">↗</span></a>}
                  <blockquote className="quote">{step.cue}</blockquote>
                  {step.note && <p className="step-note">{step.note}</p>}
                  <Check progress={progress} id={'demo-' + step.id}>Pratiquei esta etapa <span className="sr-only">· {step.title}</span></Check>
                </div>
              </li>
            ))}
          </ol>
        </section>
      )}
      <section className="section contingency" aria-labelledby="issues-title">
        <header className="section-heading">
          <div><h2 id="issues-title">Se algo falhar</h2><p>Se a correção tomar cerca de um minuto durante a apresentação, recorra ao vídeo de contingência se tiver gravado o ensaio.</p></div>
        </header>
        {troubleshooting.map(({ title, action, command }) => (
          <Detail title={title} key={title}><p>{action}</p><Command value={command} /></Detail>
        ))}
      </section>
    </div>
  )
}
