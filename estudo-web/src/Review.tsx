import { useEffect, useRef, useState } from 'react'
import { flashcards, glossary, quiz } from './content/review'
import { presenters, slides, type Scope } from './content/slides'
import { slideLink, type ReviewPage } from './route'
import { Detail, Meter, twoDigits } from './ui'

const tabs: { id: ReviewPage; title: string; description: string }[] = [
  { id: 'flashcards', title: 'Flashcards', description: 'Pense na resposta e vire o cartão para conferir.' },
  { id: 'quiz', title: 'Quiz', description: 'Uma situação por slide, com explicação após cada resposta.' },
  { id: 'banca', title: 'Perguntas de banca', description: 'Responda em voz alta antes de revelar a resposta de apoio.' },
  { id: 'glossario', title: 'Glossário', description: 'Encontre os termos técnicos usados no seminário.' },
]

function Flashcards() {
  const [index, setIndex] = useState(0)
  const [revealed, setRevealed] = useState(false)
  const card = flashcards[index]

  function selectCard(next: number) {
    setIndex(next)
    setRevealed(false)
  }

  return (
    <section className="exercise" aria-labelledby="flashcard-question">
      <div className="surface flashcard">
        <div className="exercise-meta"><span>Cartão {twoDigits(index + 1)} de {flashcards.length}</span></div>
        <h2 id="flashcard-question" aria-live="polite">{card.front}</h2>
        <div className="flashcard-answer" id="flashcard-answer" hidden={!revealed}><p>{card.back}</p></div>
        <button type="button" className="button button-primary" aria-expanded={revealed} aria-controls="flashcard-answer"
          onClick={() => setRevealed(!revealed)}>{revealed ? 'Ocultar resposta' : 'Revelar resposta'}</button>
      </div>
      <div className="exercise-navigation">
        <button className="button button-secondary" type="button" disabled={index === 0}
          onClick={() => selectCard(index - 1)}><span aria-hidden="true">←</span> Anterior</button>
        <Meter value={index + 1} max={flashcards.length} label="Posição nos flashcards" />
        <button className="button button-secondary" type="button"
          onClick={() => selectCard((index + 1) % flashcards.length)}>
          {index === flashcards.length - 1 ? 'Primeiro' : 'Próximo'} <span aria-hidden="true">→</span>
        </button>
      </div>
    </section>
  )
}

function Quiz() {
  const [answers, setAnswers] = useState<number[]>([])
  const [selection, setSelection] = useState<number | null>(null)
  const [submitted, setSubmitted] = useState(false)
  const heading = useRef<HTMLHeadingElement>(null)
  const index = answers.length
  const item = quiz[index]

  useEffect(() => {
    if (index > 0) heading.current?.focus()
  }, [index])

  if (!item) {
    const missed = quiz.filter((question, position) => question.correct !== answers[position])
    return (
      <section className="surface quiz-result" aria-labelledby="quiz-result-title">
        <p className="eyebrow">Resultado do quiz</p>
        <h2 id="quiz-result-title" tabIndex={-1} ref={heading}>{quiz.length - missed.length}/{quiz.length} acertos</h2>
        {missed.length > 0 ? (
          <div>
            <h3>Slides para revisar</h3>
            <ul>{missed.map(({ slide }) => (
              <li key={slide}><a className="text-link" href={slideLink(slide)}>Slide {twoDigits(slide)} · {slides[slide - 1].title}</a></li>
            ))}</ul>
          </div>
        ) : <p>Pratique uma explicação oral com as perguntas de banca.</p>}
        <div className="button-group">
          <button className="button button-primary" type="button" onClick={() => setAnswers([])}>Refazer quiz</button>
          <a className="button button-secondary" href="#/revisao/banca">Ir para banca <span aria-hidden="true">→</span></a>
        </div>
      </section>
    )
  }

  function nextQuestion() {
    if (selection === null) return
    setAnswers([...answers, selection])
    setSelection(null)
    setSubmitted(false)
  }

  return (
    <section className="surface exercise quiz" aria-labelledby="quiz-question">
      <div className="exercise-meta">
        <span>Questão {twoDigits(index + 1)} de {quiz.length}</span>
        <a className="text-link" href={slideLink(item.slide)}>Slide {twoDigits(item.slide)} <span aria-hidden="true">↗</span></a>
      </div>
      <Meter value={index + Number(submitted)} max={quiz.length} label="Questões respondidas" />
      <h2 id="quiz-question" tabIndex={-1} ref={heading}>{item.question}</h2>
      <form onSubmit={(event) => { event.preventDefault(); if (selection !== null) setSubmitted(true) }}>
        <fieldset className="quiz-choices" disabled={submitted}>
          <legend className="sr-only">Escolha uma resposta</legend>
          {item.choices.map((choice, choiceIndex) => {
            const isRight = submitted && choiceIndex === item.correct
            const isWrong = submitted && choiceIndex === selection && !isRight
            return (
              <label key={choice} className={'choice' + (isRight ? ' right' : isWrong ? ' wrong' : '')}>
                <input type="radio" name="quiz-choice" checked={selection === choiceIndex} onChange={() => setSelection(choiceIndex)} />
                <span>{choice}</span>
                {isRight && <span className="choice-mark">Correta</span>}
                {isWrong && <span className="choice-mark">Sua escolha</span>}
              </label>
            )
          })}
        </fieldset>
        {submitted ? (
          <>
            <div className={'quiz-feedback ' + (selection === item.correct ? 'right' : 'wrong')} role="status">
              <strong>{selection === item.correct ? 'Resposta correta' : 'Revise a resposta'}</strong>
              <p>{item.explanation}</p>
            </div>
            <button className="button button-primary" type="button" onClick={nextQuestion}>
              {index + 1 === quiz.length ? 'Ver resultado' : 'Próxima questão'} <span aria-hidden="true">→</span>
            </button>
          </>
        ) : <button className="button button-primary" type="submit" disabled={selection === null}>Conferir resposta</button>}
      </form>
    </section>
  )
}

function Banca() {
  const [scope, setScope] = useState<Scope>('all')
  return (
    <section className="banca" aria-label="Questões e respostas">
      <div className="mode-selector filter-small" role="group" aria-label="Filtrar perguntas por apresentador">
        <button type="button" aria-pressed={scope === 'all'} onClick={() => setScope('all')}>Todos</button>
        <button type="button" aria-pressed={scope === 'luiz'} onClick={() => setScope('luiz')}>Luiz</button>
        <button type="button" aria-pressed={scope === 'yahn'} onClick={() => setScope('yahn')}>Yahn</button>
      </div>
      {slides.filter((slide) => scope === 'all' || slide.presenter === scope).map((slide) => (
        <Detail key={slide.id} title={
          <span className="banca-question">
            <small>Slide {twoDigits(slide.id)} · {presenters[slide.presenter].label}</small>
            <strong>{slide.question.prompt}</strong>
          </span>
        }>
          <p>{slide.question.answer}</p>
          {slide.question.extension && <p className="extension"><strong>Ampliação didática</strong> {slide.question.extension}</p>}
          <a className="text-link" href={slideLink(slide.id, scope)}>Rever slide <span aria-hidden="true">→</span></a>
        </Detail>
      ))}
    </section>
  )
}

function normalize(value: string) {
  return value.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
}

function Glossary() {
  const [query, setQuery] = useState('')
  const filter = normalize(query.trim())
  const entries = glossary.filter(({ term, definition }) => normalize(term + ' ' + definition).includes(filter))

  return (
    <section aria-label="Termos do seminário">
      <div className="glossary-toolbar">
        <label htmlFor="glossary-search">Buscar no glossário</label>
        <input type="search" id="glossary-search" value={query} onChange={(event) => setQuery(event.target.value)}
          placeholder="Ex. checkpoint, índice, Lens" aria-controls="glossary-results" />
        <p role="status">{entries.length} {entries.length === 1 ? 'termo encontrado' : 'termos encontrados'}</p>
      </div>
      <dl className="glossary-grid" id="glossary-results">
        {entries.map(({ term, definition }) => (
          <div key={term} className="surface glossary-entry"><dt>{term}</dt><dd>{definition}</dd></div>
        ))}
      </dl>
      {!entries.length && <p>Busque por outro termo ou limpe a pesquisa.</p>}
    </section>
  )
}

export function Review({ view }: { view: ReviewPage }) {
  const tab = tabs.find((entry) => entry.id === view)!

  return (
    <div className="review">
      <header className="page-intro">
        <p className="eyebrow">Revisão do seminário</p>
        <h1>{tab.title}</h1>
        <p>{tab.description}</p>
      </header>
      <nav className="page-tabs" aria-label="Ferramentas de revisão">
        {tabs.map((item) => (
          <a href={'#/revisao/' + item.id} key={item.id} aria-current={item.id === view ? 'page' : undefined}>{item.title}</a>
        ))}
      </nav>
      {view === 'flashcards' && <Flashcards />}
      {view === 'quiz' && <Quiz />}
      {view === 'banca' && <Banca />}
      {view === 'glossario' && <Glossary />}
    </div>
  )
}
