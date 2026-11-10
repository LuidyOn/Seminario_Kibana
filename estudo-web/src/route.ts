import { slides, type Scope } from './content/slides'

export type ReviewPage = 'flashcards' | 'quiz' | 'banca' | 'glossario'
export type DemoPage = 'preparacao' | 'roteiro'

export type Route =
  | { page: 'home' | 'sources' | 'missing' }
  | { page: 'slides'; id: number; scope: Scope }
  | { page: 'demo'; view: DemoPage }
  | { page: 'review'; view: ReviewPage }

export function slideLink(id: number, scope: Scope = 'all') {
  return '#/slides/' + id + (scope === 'all' ? '' : '?parte=' + scope)
}

export function parseRoute(hash: string): Route {
  const [path, search] = hash.slice(1).split('?', 2)
  if (!path || path === '/') return { page: 'home' }
  if (path === '/fontes') return { page: 'sources' }

  const slidePath = /^\/slides\/(\d+)$/.exec(path)
  if (path === '/slides' || slidePath) {
    const id = Number(slidePath?.[1] ?? 1)
    if (!slides.some((slide) => slide.id === id)) return { page: 'missing' }
    const scope = new URLSearchParams(search).get('parte')
    return { page: 'slides', id, scope: scope === 'luiz' || scope === 'yahn' ? scope : 'all' }
  }

  if (path === '/demo' || path === '/demo/roteiro') return { page: 'demo', view: 'roteiro' }
  if (path === '/demo/preparacao') return { page: 'demo', view: 'preparacao' }
  if (path === '/revisao' || path === '/revisao/flashcards') return { page: 'review', view: 'flashcards' }
  if (path === '/revisao/quiz') return { page: 'review', view: 'quiz' }
  if (path === '/revisao/banca') return { page: 'review', view: 'banca' }
  if (path === '/revisao/glossario') return { page: 'review', view: 'glossario' }
  return { page: 'missing' }
}
