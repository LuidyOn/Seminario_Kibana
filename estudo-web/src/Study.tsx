import { useEffect, useState } from 'react'
import { presenters, slides, type Scope, type TimedSlide } from './content/slides'
import type { Progress } from './progress'
import { slideLink } from './route'
import { Capture, Check, Detail, formatTime, Stopwatch, twoDigits } from './ui'

export type StudyMode = 'study' | 'rehearse'

const scopes: { id: Scope; label: string; description: string }[] = [
  { id: 'all', label: 'Apresentação completa', description: 'Todos os 12 slides' },
  { id: 'luiz', label: 'Minha parte: Luiz', description: 'Ímpares + demonstração' },
  { id: 'yahn', label: 'Minha parte: Yahn', description: 'Pares' },
]

function Speech({ slide }: { slide: TimedSlide }) {
  return <div className="speech">{slide.speech.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</div>
}

function SlideContent({ slide, mode, context, onExpand }: {
  slide: TimedSlide; mode: StudyMode; context: boolean; onExpand: () => void
}) {
  const [speechShown, setSpeechShown] = useState(false)
  const speaker = presenters[slide.presenter]
  if (context) {
    return (
      <section className="surface context-card" aria-labelledby="context-title">
        <h2 id="context-title">Contexto da fala de {speaker.label}</h2>
        <p>{slide.shows}</p>
        <h3>Passagem de fala</h3>
        <p>{slide.transition}</p>
        <button type="button" className="button button-secondary" onClick={onExpand}>Ver estudo completo</button>
      </section>
    )
  }

  return (
    <div className="slide-content">
      {mode === 'rehearse' && (
        <section className="surface rehearsal" aria-labelledby="rehearsal-title">
          <div className="rehearsal-header">
            <div><h2 id="rehearsal-title">Ensaie a fala</h2><p>Use as pistas, cronometre e confira sua versão.</p></div>
            <Stopwatch target={slide.seconds} />
          </div>
          <ul className="cue-list">{slide.cues.map((cue) => <li key={cue}>{cue}</li>)}</ul>
          <button type="button" className="button button-secondary" aria-expanded={speechShown}
            aria-controls="rehearsal-speech" onClick={() => setSpeechShown(!speechShown)}>
            {speechShown ? 'Ocultar fala' : 'Mostrar fala'}
          </button>
          <div id="rehearsal-speech" hidden={!speechShown}>{speechShown && <Speech slide={slide} />}</div>
        </section>
      )}
      <Detail title="O que o slide mostra" initiallyOpen={mode === 'study'}>
        <p>{slide.shows}</p>
        {slide.capture && <Capture name={slide.capture} />}
        {slide.example && (
          <figure className="code-figure"><figcaption>Exemplo de formato do slide</figcaption><pre><code>{slide.example}</code></pre></figure>
        )}
        {slide.id === 3 && (
          <div className="architecture">
            <div><strong>No Windows</strong><p>Event Log → PowerShell → JSONL</p></div>
            <div><strong>Nos containers</strong><p>Logstash → Elasticsearch ↔ Kibana</p></div>
          </div>
        )}
      </Detail>
      <Detail title="Conceitos que devo entender" initiallyOpen={mode === 'study'}>
        <dl className="concepts">
          {slide.concepts.map(({ term, explanation }) => (
            <div key={term}><dt>{term}</dt><dd>{explanation}</dd></div>
          ))}
        </dl>
      </Detail>
      {mode === 'study' && <Detail title="Fala sugerida"><Speech slide={slide} /></Detail>}
      <Detail title="Conexão com a prática" initiallyOpen={slide.id === 11 && mode === 'study'}>
        <p>{slide.practice}</p>
        {slide.id === 11 && (
          <div className="button-group">
            <a className="button button-secondary button-small" href="#/demo/preparacao">Preparação prévia</a>
            <a className="button button-primary button-small" href="#/demo/roteiro">Roteiro da demo <span aria-hidden="true">→</span></a>
          </div>
        )}
      </Detail>
      <Detail title="Transição"><p className="quote">{slide.transition}</p></Detail>
      <Detail title="Pergunta provável do professor">
        <p><strong>{slide.question.prompt}</strong></p>
        <Detail title="Ver resposta">
          <p>{slide.question.answer}</p>
          {slide.question.extension && <p className="extension"><strong>Ampliação didática</strong> {slide.question.extension}</p>}
        </Detail>
      </Detail>
    </div>
  )
}

export function Study({ id, scope, mode, onMode, progress }: {
  id: number; scope: Scope; mode: StudyMode; onMode: (mode: StudyMode) => void; progress: Progress
}) {
  const slide = slides[id - 1]
  const speaker = presenters[slide.presenter]
  const [expandedContext, setExpandedContext] = useState(false)
  const [showIndex, setShowIndex] = useState(false)
  const context = scope !== 'all' && scope !== slide.presenter && !expandedContext
  const previous = slides[id - 2]
  const next = slides[id]

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return
      if (event.target instanceof HTMLElement && event.target.closest('a, button, input, select, textarea, summary, [contenteditable]')) return
      if (window.getSelection()?.toString()) return
      const destination = event.key === 'ArrowLeft' ? previous : event.key === 'ArrowRight' ? next : undefined
      if (!destination) return
      event.preventDefault()
      window.location.hash = slideLink(destination.id, scope)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [previous, next, scope])

  return (
    <div className="study">
      <div className="study-toolbar">
        <nav className="scope-selector" aria-label="Filtrar slides por apresentador">
          {scopes.map(({ id: option, label, description }) => (
            <a key={option} href={slideLink(option === 'all' || option === slide.presenter ? id : presenters[option].first, option)}
              className={'scope-option ' + (option === scope ? 'active' : '')}
              aria-current={option === scope ? 'true' : undefined}>
              <strong>{label}</strong><small>{description}</small>
            </a>
          ))}
        </nav>
        <div className="mode-selector" role="group" aria-label="Modo de estudo">
          <button type="button" aria-pressed={mode === 'study'} onClick={() => onMode('study')}>Estudar</button>
          <button type="button" aria-pressed={mode === 'rehearse'} onClick={() => onMode('rehearse')}>Ensaiar</button>
        </div>
      </div>
      <div className="study-layout">
        <aside className="slide-rail">
          <div className="rail-heading"><h2>Roteiro por slide</h2><span>01–12</span></div>
          <button type="button" className="button button-secondary index-toggle" aria-expanded={showIndex}
            aria-controls="slide-index" onClick={() => setShowIndex(!showIndex)}>
            {showIndex ? 'Ocultar índice' : 'Ver os 12 slides'} <span aria-hidden="true">{showIndex ? '−' : '+'}</span>
          </button>
          <nav id="slide-index" className={'slide-index' + (showIndex ? ' is-open' : '')} aria-label="Índice dos slides">
            <ol>
              {slides.map((item) => {
                const studied = progress.checked('slide-' + item.id)
                const other = scope !== 'all' && item.presenter !== scope
                return (
                  <li key={item.id}>
                    <a href={slideLink(item.id, scope)} aria-current={item.id === id ? 'page' : undefined}
                      className={other ? 'context-slide' : undefined}>
                      <span className="slide-number">{twoDigits(item.id)}</span>
                      <span className="index-text">
                        <strong>{item.title}</strong>
                        <small>{presenters[item.presenter].label}{other && ' · Contexto'}</small>
                      </span>
                      <span className={'slide-state ' + (studied ? 'complete' : item.presenter)}
                        aria-label={studied ? 'Estudado' : 'Pendente'}>{studied ? '✓' : '•'}</span>
                    </a>
                  </li>
                )
              })}
            </ol>
          </nav>
        </aside>
        <article className="slide-article">
          <header className={'slide-heading ' + slide.presenter}>
            <p className="eyebrow">Slide {twoDigits(slide.id)} <span /> {speaker.name}</p>
            <div className="slide-title"><h1>{slide.title}</h1><span className="stage-chip">{slide.stage.name}</span></div>
            <p>{slide.summary}</p>
            <div className="slide-meta">
              <span className="time-chip">{formatTime(slide.start)}–{formatTime(slide.end)}</span>
              <span>Tempo sugerido {formatTime(slide.seconds)}</span>
            </div>
          </header>
          <SlideContent key={mode} slide={slide} mode={mode} context={context} onExpand={() => setExpandedContext(true)} />
          <div className="study-check">
            <Check progress={progress} id={'slide-' + slide.id}>Marcar slide como estudado</Check>
          </div>
          <nav className="pager" aria-label="Navegar entre slides">
            {previous
              ? <a href={slideLink(previous.id, scope)} className="button button-secondary"><span aria-hidden="true">←</span> Anterior</a>
              : <a href="#/" className="button button-secondary"><span aria-hidden="true">←</span> Visão geral</a>}
            <span className="keyboard-hint"><kbd>←</kbd> <kbd>→</kbd></span>
            {next
              ? <a href={slideLink(next.id, scope)} className="button button-primary">Próximo <span aria-hidden="true">→</span></a>
              : <a href="#/revisao/banca" className="button button-primary">Revisar banca <span aria-hidden="true">→</span></a>}
          </nav>
        </article>
      </div>
    </div>
  )
}
