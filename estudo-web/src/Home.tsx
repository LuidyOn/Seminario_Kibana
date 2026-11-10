import { presenters, slides, stages, totalSeconds, type Presenter } from './content/slides'
import type { Progress } from './progress'
import { slideLink } from './route'
import { Capture, formatTime, Meter, twoDigits } from './ui'

export function Home({ progress }: { progress: Progress }) {
  return (
    <>
      <section className="hero" aria-labelledby="home-title">
        <div className="hero-copy">
          <p className="eyebrow">Seminário técnico <span /> UniSales 2026</p>
          <h1 id="home-title">Kibana <span>Guia interativo do seminário</span></h1>
          <p className="hero-description">Acompanhe os eventos do Windows até o dashboard. Estude a sua parte, ensaie as falas e pratique a demonstração.</p>
          <div className="button-group hero-actions">
            <a className="button button-primary" href={slideLink(1)}>Começar estudo <span aria-hidden="true">→</span></a>
            <a className="button button-secondary" href="#/demo/roteiro"><span className="play-icon" aria-hidden="true" /> Roteiro da demo</a>
          </div>
          <dl className="hero-stats">
            <div><dt>Slides</dt><dd>{slides.length}</dd></div>
            <div><dt>Apresentação</dt><dd>{totalSeconds / 60} <span>min</span></dd></div>
            <div><dt>Demo</dt><dd>5 <span>min</span></dd></div>
          </dl>
        </div>
        <div className="hero-art"><Capture name="dashboard" hero /></div>
      </section>
      <section className="section story" aria-labelledby="story-title">
        <header className="section-heading">
          <div><h2 id="story-title">Da situação-problema à resposta</h2><p>Abra qualquer etapa para continuar a história.</p></div>
          <a className="text-link" href={slideLink(1)}>Ver todos os slides <span aria-hidden="true">→</span></a>
        </header>
        <ol className="story-list">
          {stages.map((stage, index) => {
            const last = (stages[index + 1]?.first ?? slides.length + 1) - 1
            return (
              <li key={stage.first}>
                <a href={slideLink(stage.first)}>
                  <span className="story-dot" aria-hidden="true" />
                  <span>{stage.name}</span>
                  <small>{last === stage.first ? 'Slide ' + twoDigits(last) : 'Slides ' + twoDigits(stage.first) + '–' + twoDigits(last)}</small>
                </a>
              </li>
            )
          })}
        </ol>
      </section>
      <section className="section" aria-labelledby="people-title">
        <header className="section-heading">
          <div><h2 id="people-title">Escolha sua parte</h2><p>Estude suas falas com o contexto dos outros slides à mão.</p></div>
        </header>
        <div className="presenter-grid">
          {(Object.keys(presenters) as Presenter[]).map((key) => {
            const presenter = presenters[key]
            const part = slides.filter((slide) => slide.presenter === key)
            const studied = part.filter(({ id }) => progress.checked('slide-' + id)).length
            return (
              <article className={'presenter-card ' + key} key={key}>
                <div className="presenter-top">
                  <span className="avatar" aria-hidden="true">{key === 'luiz' ? 'LO' : 'YF'}</span>
                  <div><h3>{presenter.name}</h3><p>{presenter.part}</p></div>
                  <span className="time-chip" title="Tempo estimado">{formatTime(part.reduce((sum, slide) => sum + slide.seconds, 0))}</span>
                </div>
                <ul className="presenter-slides" aria-label={'Slides de ' + presenter.label}>
                  {part.map(({ id, title }) => (
                    <li key={id}>
                      <a className={progress.checked('slide-' + id) ? 'studied' : undefined}
                        href={slideLink(id, key)} aria-label={'Slide ' + id + ' · ' + title}>{twoDigits(id)}</a>
                    </li>
                  ))}
                </ul>
                <div className="presenter-progress">
                  <span>{studied}/{part.length} estudados</span>
                  <Meter value={studied} max={part.length} label={'Slides estudados por ' + presenter.label} tone={key === 'luiz' ? 'blue' : 'red'} />
                </div>
                <a className="text-link" href={slideLink(presenter.first, key)}>Estudar parte de {presenter.label} <span aria-hidden="true">→</span></a>
              </article>
            )
          })}
        </div>
      </section>
      <section className="section" aria-labelledby="review-links-title">
        <header className="section-heading">
          <div><h2 id="review-links-title">Teste o que você consegue explicar</h2></div>
        </header>
        <div className="review-links">
          {[
            ['flashcards', 'Flashcards', 'Recupere um conceito de memória.'],
            ['quiz', 'Quiz', 'Resolva uma questão de cada slide.'],
            ['banca', 'Perguntas de banca', 'Pratique respostas curtas.'],
            ['glossario', 'Glossário', 'Encontre o termo certo.'],
          ].map(([path, title, description]) => (
            <a href={'#/revisao/' + path} key={path}>
              <strong>{title} <span aria-hidden="true">↗</span></strong>
              <span>{description}</span>
            </a>
          ))}
        </div>
      </section>
    </>
  )
}
