import { Moon, Sun, Laptop } from 'lucide-react'
import { useTheme } from './ThemeProvider'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const options = [
    { k: 'light', Icon: Sun, label: 'Hell' },
    { k: 'dark', Icon: Moon, label: 'Dunkel' },
    { k: 'system', Icon: Laptop, label: 'System' },
  ]

  return (
    <div className="glass-surface rounded-xl p-1 flex">
      {options.map(({ k, Icon, label }) => (
        <button
          key={k}
          onClick={() => setTheme(k)}
          className={`px-2 py-1 rounded-lg text-xs font-semibold inline-flex items-center gap-1 transition
            ${theme === k ? 'bg-white/70 dark:bg-white/10 text-brand-navy' : 'text-slate-600 hover:bg-white/60 dark:hover:bg-white/10'}`}
          aria-pressed={theme === k}
          title={label}
        >
          <Icon className="h-4 w-4" />
        </button>
      ))}
    </div>
  )
}
