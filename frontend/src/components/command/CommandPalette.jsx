import * as React from 'react'
import { useNavigate } from 'react-router-dom'
import { Command } from 'cmdk'
import { Search, LayoutDashboard, BadgeEuro, FileText } from 'lucide-react'

const commands = [
  { id: 'home', label: 'Gehe zu Übersicht', shortcut: 'G', to: '/', icon: LayoutDashboard },
  { id: 'search', label: 'Suche öffnen', shortcut: 'S', to: '/search', icon: Search },
  { id: 'funding', label: 'Förderungen anzeigen', shortcut: 'F', to: '/funding', icon: BadgeEuro },
  { id: 'apps', label: 'Anträge anzeigen', shortcut: 'A', to: '/applications', icon: FileText },
]

export function CommandPalette({ open, onOpenChange }) {
  const [value, setValue] = React.useState('')
  const navigate = useNavigate()

  React.useEffect(() => {
    function down(e) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        onOpenChange(!open)
      }
      // quick combos
      const cmd = commands.find(c => c.shortcut?.toLowerCase() === e.key.toLowerCase())
      if (open && cmd) {
        navigate(cmd.to)
        onOpenChange(false)
      }
    }
    window.addEventListener('keydown', down)
    return () => window.removeEventListener('keydown', down)
  }, [open, onOpenChange, navigate])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-start pt-[10vh] px-4 bg-slate-900/50 backdrop-blur-sm"
      onClick={() => onOpenChange(false)}
    >
      <Command
        onKeyDown={(e) => e.stopPropagation()}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-xl rounded-2xl border border-slate-900/10 bg-white/90 dark:bg-slate-900/90 shadow-elevated backdrop-blur-xl"
      >
        <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-900/10">
          <Search className="h-4 w-4 text-slate-400" />
          <Command.Input
            autoFocus
            value={value}
            onValueChange={setValue}
            placeholder="Suchen oder springen…"
            className="w-full bg-transparent outline-none placeholder:text-slate-400 text-slate-900 dark:text-slate-100"
          />
          <kbd className="kbd">Esc</kbd>
        </div>
        <Command.List className="max-h-[50vh] overflow-y-auto py-2">
          <Command.Empty className="px-4 py-2 text-sm text-slate-500">Keine Ergebnisse</Command.Empty>
          <Command.Group heading="Navigation" className="px-2">
            {commands.map((c) => (
              <Command.Item
                key={c.id}
                value={c.label}
                onSelect={() => { navigate(c.to); onOpenChange(false) }}
                className="flex items-center gap-3 px-3 py-2 rounded-xl data-[selected=true]:bg-slate-100 dark:data-[selected=true]:bg-white/10 cursor-pointer"
              >
                <c.icon className="h-4 w-4 text-slate-500" />
                <span className="text-slate-800 dark:text-slate-100">{c.label}</span>
                <span className="ml-auto text-xs text-slate-400">⌘{c.shortcut}</span>
              </Command.Item>
            ))}
          </Command.Group>
        </Command.List>
      </Command>
    </div>
  )
}
