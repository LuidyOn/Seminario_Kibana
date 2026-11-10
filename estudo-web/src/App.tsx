import { useEffect, useRef, useState, useSyncExternalStore } from 'react'
import { Demo } from './Demo'
import { Home } from './Home'
import { Review } from './Review'
import { Study, type StudyMode } from './Study'
import { slides } from './content/slides'
import { officialSources, projectSources } from './content/sources'
import { useProgress } from './progress'
import { parseRoute, slideLink } from './route'

const navigation = [
  { page: 'home', href: '#/', label: 'Visão geral' },
  { page: 'slides', href: slideLink(1), label: 'Slides' },
  { page: 'demo', href: '#/demo/roteiro', label: 'Demonstração' },
  { page: 'review', href: '#/revisao/flashcards', label: 'Revisão' },
]

function subscribeToHash(listener: () => void) {
  window.addEventListener('hashchange', listener)
  return () => window.removeEventListener('hashchange', listener)
}

function currentHash() {
  return window.location.hash
}

function Sources() {
  return (
    <div className="sources">
      <header className="page-intro"><h1>Fontes do seminário</h1><p>Material consultado para os slides, as falas e a prática.</p></header>
      <section className="surface source-card" aria-labelledby="project-sources">
        <h2 id="project-sources">Documentos do projeto</h2>
        <dl className="concepts">
          {projectSources.map(({ path, use }) => <div key={path}><dt><code>{path}</code></dt><dd>{use}</dd></div>)}
        </dl>
      </section>
      <section className="surface source-card" aria-labelledby="reading-notes">
        <h2 id="reading-notes">Notas sobre as fontes</h2>
        <p>O roteiro de apresentação sugere Luiz nos slides 1 a 5 e Yahn nos 6 a 10. A nota da demo prevê duas pessoas entre operação e narração. Este guia segue a divisão definida para o ensaio. Luiz conduz os ímpares e executa a demo. Yahn conduz os pares e as perguntas.</p>
        <p>O índice das imagens em slides/assets/README.md cita os slides 5 e 9 para o Discover e o dashboard. No PowerPoint definitivo, as capturas estão nos slides 8 e 11. Os totais nas imagens são históricos e dependem do computador e do período.</p>
      </section>
      <section className="surface source-card" aria-labelledby="official-sources">
        <h2 id="official-sources">Documentação oficial</h2>
        <ul className="source-links">
          {officialSources.map(({ label, url }) => (
            <li key={url}><a className="text-link" href={url} target="_blank" rel="noreferrer">{label} <span aria-hidden="true">↗</span></a></li>
          ))}
        </ul>
      </section>
    </div>
  )
}

export default function App() {
  const hash = useSyncExternalStore(subscribeToHash, currentHash)
  const route = parseRoute(hash)
  const [mode, setMode] = useState<StudyMode>('study')
  const progress = useProgress()
  const studied = slides.filter(({ id }) => progress.checked('slide-' + id)).length
  const main = useRef<HTMLElement>(null)
  const previousHash = useRef(hash)

  useEffect(() => {
    const pageTitle = main.current?.querySelector('h1')?.textContent
    document.title = route.page === 'home' ? 'Kibana — Guia interativo do seminário' : pageTitle + ' · Guia Kibana'
    if (previousHash.current !== hash) {
      previousHash.current = hash
      main.current?.focus({ preventScroll: true })
      window.scrollTo(0, 0)
    }
  }, [hash, route.page])

  return (
    <>
      <a className="skip-link" href="#conteudo" onClick={(event) => {
        event.preventDefault()
        main.current?.focus()
      }}>Ir para o conteúdo</a>
      <header className="site-header">
        <div className="wrap header-inner">
          <a href="#/" className="brand" aria-label="Kibana · Visão geral">
            <span className="brand-mark" aria-hidden="true"><i /><i /><i /><i /></span>
            <span><strong>Kibana</strong><small>Seminário 2026</small></span>
          </a>
          <nav className="main-nav" aria-label="Navegação principal">
            {navigation.map(({ page, href, label }) => (
              <a href={href} aria-current={page === route.page ? 'page' : undefined} key={page}>{label}</a>
            ))}
          </nav>
          <a className="header-progress" href={slideLink(1)} aria-label={studied + ' de ' + slides.length + ' slides estudados'}>
            <span aria-hidden="true">✓</span> {studied}/{slides.length} <span className="header-progress-label">estudados</span>
          </a>
        </div>
      </header>
      <main id="conteudo" ref={main} tabIndex={-1} className="wrap site-main">
        {route.page === 'home' && <Home progress={progress} />}
        {route.page === 'slides' && <Study key={route.id + route.scope} id={route.id} scope={route.scope} mode={mode} onMode={setMode} progress={progress} />}
        {route.page === 'demo' && <Demo view={route.view} progress={progress} />}
        {route.page === 'review' && <Review view={route.view} />}
        {route.page === 'sources' && <Sources />}
        {route.page === 'missing' && <section className="page-intro"><h1>Página não encontrada</h1><a className="button button-primary" href="#/">Voltar à visão geral</a></section>}
      </main>
      <footer className="site-footer">
        <div className="wrap footer-inner">
          <div><strong>Seminário Kibana</strong><p>{progress.persistent ? 'O progresso fica neste navegador.' : 'O navegador bloqueou o armazenamento local. O progresso vale nesta sessão.'}</p></div>
          <a className="text-link" href="#/fontes">Fontes do seminário <span aria-hidden="true">→</span></a>
        </div>
      </footer>
    </>
  )
}
