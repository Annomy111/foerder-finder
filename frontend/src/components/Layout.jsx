import { NavLink, useNavigate } from 'react-router-dom'
import { useMemo, useState } from 'react'
import {
  LayoutDashboard,
  Search,
  BadgeEuro,
  FileText,
  LogOut,
  Sparkles,
} from 'lucide-react'
import clsx from 'clsx'
import useAuthStore from '@/store/authStore'
import { CommandPalette } from './command/CommandPalette'
import { ThemeToggle } from '@/theme/ThemeToggle'

const nav = [
  { to: '/', label: 'Übersicht', icon: LayoutDashboard },
  { to: '/search', label: 'Suche', icon: Search },
  { to: '/funding', label: 'Förderungen', icon: BadgeEuro },
  { to: '/applications', label: 'Anträge', icon: FileText },
]

export default function Layout({ children }) {
  const navigate = useNavigate()
  const { logout, user } = useAuthStore()
  const [paletteOpen, setPaletteOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const initials = useMemo(() => {
    if (!user?.email) return 'E'
    const [name] = user.email.split('@')
    if (!name) return 'E'
    return name
      .split(/[._-]/)
      .filter(Boolean)
      .slice(0, 2)
      .map((chunk) => chunk[0]?.toUpperCase())
      .join('')
      .slice(0, 2)
  }, [user?.email])

  return (
    <div className="min-h-screen pb-24 lg:pb-0">
      <div className="mx-auto flex min-h-screen w-full max-w-[1380px] gap-6 px-4 sm:px-6 lg:px-8">
        <aside className="hidden lg:flex w-60 flex-col py-10">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-3 rounded-3xl border border-white/60 bg-white px-4 py-3 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-sky to-brand-green text-white shadow-md">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">EduFunds</p>
              <p className="text-lg font-semibold text-brand-navy">Förder-Cockpit</p>
            </div>
          </button>

          <nav className="mt-10 flex flex-col gap-1">
            {nav.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold transition-all',
                    isActive
                      ? 'bg-gradient-to-r from-primary-600 to-brand-green text-white shadow-md'
                      : 'text-slate-600 hover:bg-white hover:text-brand-navy'
                  )
                }
              >
                <Icon className={clsx('h-5 w-5', 'transition-colors')} />
                {label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <div className="flex-1 py-8">
          <header className="sticky top-8 z-40">
            <div className="glass-surface flex items-center gap-3 rounded-3xl px-4 py-4">
              <button
                className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/70 bg-white/80 text-brand-navy shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md lg:hidden"
                aria-label="Befehlspalette öffnen"
                onClick={() => setPaletteOpen(true)}
              >
                <Search className="h-5 w-5" />
              </button>

              <div className="flex flex-1 items-center gap-3">
                <div className="flex flex-col">
                  <p className="section-title hidden lg:block">Workspace</p>
                  <p className="text-xs font-semibold uppercase tracking-[0.35em] text-slate-500 lg:hidden">EduFunds</p>
                  <h1 className="text-sm font-semibold text-brand-navy lg:text-lg">
                    <span className="hidden lg:inline">Willkommen zurück</span>
                    <span className="lg:hidden">Förder-Cockpit</span>
                  </h1>
                </div>

                <div className="relative ml-auto w-full max-w-xl">
                  <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    onFocus={() => setPaletteOpen(true)}
                    placeholder="Schnellsuche · Förderungen, Anträge, Sucheinträge… (⌘K)"
                    className="input w-full rounded-2xl pl-11"
                  />
                </div>

                <ThemeToggle />
                <div className="hidden items-center gap-3 sm:flex">
                  <div className="text-right">
                    <p className="text-sm font-semibold text-brand-navy">{user?.email || 'Nutzer'}</p>
                    <p className="text-xs text-slate-500">{user?.role || 'Administrator'}</p>
                  </div>
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-brand-green text-white font-semibold">
                    {initials}
                  </div>
                </div>
                <button onClick={handleLogout} className="btn-secondary hidden md:inline-flex">
                  <LogOut className="h-5 w-5" />
                  Abmelden
                </button>
              </div>
            </div>
          </header>

          <main className="mt-8 space-y-8">
            {children}
          </main>
        </div>
      </div>

      <nav className="lg:hidden fixed bottom-4 left-0 right-0 z-30 flex justify-center">
        <div className="glass-surface inline-flex items-center gap-1 rounded-3xl px-4 py-2">
          {nav.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                clsx(
                  'flex flex-col items-center gap-1 rounded-2xl px-3 py-2 text-[11px] font-medium transition-colors',
                  isActive ? 'text-brand-navy' : 'text-slate-600 hover:text-brand-navy'
                )
              }
              aria-label={label}
            >
              <Icon className="h-5 w-5" />
              <span>{label}</span>
            </NavLink>
          ))}
        </div>
      </nav>

      <CommandPalette open={paletteOpen} onOpenChange={setPaletteOpen} />
    </div>
  )
}
