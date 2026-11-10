import { useEffect, useRef, useState, type ReactNode } from 'react'
import eventViewer from './assets/visualizador-eventos.webp'
import discover from './assets/discover.webp'
import dashboard from './assets/eventos-do-windows.webp'
import type { Progress } from './progress'

const captures = {
  eventViewer: {
    source: eventViewer, width: 878, height: 476,
    alt: 'Visualizador de Eventos aberto em Aplicativo, com nível, data e hora, fonte e identificação do evento. Painel de mensagens oculto.',
    title: 'Visualizador de Eventos · Aplicativo',
  },
  discover: {
    source: discover, width: 1680, height: 750,
    alt: 'Discover com Data View Eventos do Windows, filtro KQL de erros, histograma e tabela de documentos.',
    title: 'Discover · Consulta por nível Error',
  },
  dashboard: {
    source: dashboard, width: 1680, height: 888,
    alt: 'Dashboard Eventos do Windows com total, distribuição por nível, distribuição por provedor e histograma.',
    title: 'Dashboard · Eventos do Windows',
  },
}

export function twoDigits(value: number) {
  return String(value).padStart(2, '0')
}

export function formatTime(seconds: number) {
  return twoDigits(Math.floor(seconds / 60)) + ':' + twoDigits(seconds % 60)
}

export function Capture({ name, hero = false }: { name: keyof typeof captures; hero?: boolean }) {
  const capture = captures[name]
  return (
    <figure className={'capture' + (hero ? ' capture-hero' : '')}>
      <figcaption>
        <span>{capture.title}</span>
        <span className="capture-status">Captura histórica</span>
      </figcaption>
      <a href={capture.source} target="_blank" rel="noopener" aria-label={'Ampliar captura · ' + capture.title}>
        <img src={capture.source} alt={capture.alt} width={capture.width} height={capture.height}
          loading={hero ? 'eager' : 'lazy'} decoding="async" />
      </a>
    </figure>
  )
}

export function Meter({ value, max, label, tone = 'blue' }: {
  value: number; max: number; label: string; tone?: 'blue' | 'red'
}) {
  return <progress className={'meter ' + tone} value={value} max={max} aria-label={label}>{value}/{max}</progress>
}

export function Check({ progress, id, children }: { progress: Progress; id: string; children: ReactNode }) {
  return (
    <label className="check">
      <input type="checkbox" checked={progress.checked(id)}
        onChange={(event) => progress.setChecked(id, event.target.checked)} />
      <span>{children}</span>
    </label>
  )
}

export function Detail({ title, children, initiallyOpen = false }: {
  title: ReactNode; children: ReactNode; initiallyOpen?: boolean
}) {
  return (
    <details className="detail" open={initiallyOpen || undefined}>
      <summary>{title}<span aria-hidden="true" /></summary>
      <div className="detail-body">{children}</div>
    </details>
  )
}

export function Command({ value }: { value: string }) {
  const [status, setStatus] = useState<'idle' | 'copied' | 'selected' | 'manual'>('idle')
  const code = useRef<HTMLElement>(null)

  useEffect(() => {
    if (status === 'idle') return
    const timeout = window.setTimeout(() => setStatus('idle'), 3500)
    return () => window.clearTimeout(timeout)
  }, [status])

  async function copy() {
    try {
      await navigator.clipboard.writeText(value)
      setStatus('copied')
    } catch {
      const selection = window.getSelection()
      if (code.current && selection) {
        const range = document.createRange()
        range.selectNodeContents(code.current)
        selection.removeAllRanges()
        selection.addRange(range)
        setStatus('selected')
      } else {
        setStatus('manual')
      }
    }
  }

  return (
    <div className="command">
      <code ref={code}>{value}</code>
      <button type="button" className="button button-quiet button-small" aria-label={'Copiar ' + value} onClick={copy}>
        {status === 'copied' ? 'Copiado' : 'Copiar'}
      </button>
      <span className={status === 'selected' || status === 'manual' ? 'command-status' : 'sr-only'} role="status">
        {status === 'copied' && 'Copiado para a área de transferência.'}
        {status === 'selected' && 'Texto selecionado. Use Ctrl+C ou o menu de cópia.'}
        {status === 'manual' && 'Selecione o comando e copie manualmente.'}
      </span>
    </div>
  )
}

export function Stopwatch({ target }: { target: number }) {
  const [started, setStarted] = useState<number | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const [now, setNow] = useState(0)
  const running = started !== null

  useEffect(() => {
    if (!running) return
    const tick = window.setInterval(() => setNow(performance.now()), 150)
    return () => window.clearInterval(tick)
  }, [running])

  function toggle() {
    const time = performance.now()
    if (started === null) {
      setNow(time)
      setStarted(time)
    } else {
      setElapsed(elapsed + time - started)
      setStarted(null)
    }
  }

  function reset() {
    setStarted(null)
    setElapsed(0)
  }

  const seconds = Math.floor((elapsed + (started === null ? 0 : now - started)) / 1000)
  return (
    <div className="stopwatch">
      <div className="stopwatch-time">
        <span role="timer" aria-label="Tempo decorrido" className={seconds >= target ? 'time-past' : undefined}>
          {formatTime(seconds)}
        </span>
        <small>Meta {formatTime(target)}</small>
      </div>
      <div className="button-group">
        <button className="button button-primary button-small" type="button" onClick={toggle}>
          {running ? 'Pausar' : elapsed > 0 ? 'Retomar' : 'Iniciar'}
        </button>
        <button className="button button-secondary button-small" type="button" onClick={reset}>Zerar</button>
      </div>
    </div>
  )
}
