import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const ThemeContext = createContext({
  theme: 'system',
  setTheme: () => {},
})

export function ThemeProvider({ children, defaultTheme = 'system' }) {
  const [theme, setTheme] = useState(
    () => localStorage.getItem('theme') || defaultTheme
  )

  useEffect(() => {
    const root = document.documentElement
    const mq = window.matchMedia('(prefers-color-scheme: dark)')

    function apply(t) {
      const next = t === 'system' ? (mq.matches ? 'dark' : 'light') : t
      root.setAttribute('data-theme', next)
      localStorage.setItem('theme', t)
    }
    apply(theme)

    const onChange = () => theme === 'system' && apply('system')
    mq.addEventListener?.('change', onChange)
    return () => mq.removeEventListener?.('change', onChange)
  }, [theme])

  const value = useMemo(() => ({ theme, setTheme }), [theme])
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  return useContext(ThemeContext)
}
