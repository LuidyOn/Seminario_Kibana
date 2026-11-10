import { useEffect, useState } from 'react'
import { demoSteps, preparation } from './content/demo'
import { slides } from './content/slides'

const storageKey = 'seminario-kibana:checklist:v1'
const validKeys = new Set([
  ...slides.map(({ id }) => 'slide-' + id),
  ...preparation.map(({ id }) => 'prep-' + id),
  ...demoSteps.map(({ id }) => 'demo-' + id),
])

function readChecks(): Record<string, true> | null {
  try {
    const data: unknown = JSON.parse(localStorage.getItem(storageKey) ?? '{}')
    if (data === null || typeof data !== 'object' || Array.isArray(data)) return {}
    return Object.fromEntries(
      Object.entries(data).filter(([key, value]) => validKeys.has(key) && value === true),
    )
  } catch {
    return null
  }
}

export function useProgress() {
  const [checks, setChecks] = useState(() => readChecks() ?? {})
  const [persistent, setPersistent] = useState(() => readChecks() !== null)

  useEffect(() => {
    function sync(event: StorageEvent) {
      if (event.key === storageKey || event.key === null) setChecks(readChecks() ?? {})
    }
    window.addEventListener('storage', sync)
    return () => window.removeEventListener('storage', sync)
  }, [])

  function setChecked(key: string, checked: boolean) {
    const updated = { ...(readChecks() ?? checks) }
    if (checked) updated[key] = true
    else delete updated[key]

    try {
      localStorage.setItem(storageKey, JSON.stringify(updated))
      setPersistent(true)
    } catch {
      setPersistent(false)
    }
    setChecks(updated)
  }

  return {
    persistent,
    checked: (key: string) => checks[key] === true,
    setChecked,
  }
}

export type Progress = ReturnType<typeof useProgress>
