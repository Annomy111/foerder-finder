import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '@/store/authStore'
import { authAPI } from '@/services/api'
import { AlertCircle, Loader2, Sparkles, TrendingUp, Users } from 'lucide-react'

export default function LoginPage() {
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const response = await authAPI.login(email, password)

      login(
        {
          user_id: response.user_id,
          school_id: response.school_id,
          email,
          role: response.role,
        },
        response.access_token,
      )

      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login fehlgeschlagen')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-bg min-h-screen grid lg:grid-cols-2">
      <div className="hidden lg:flex relative p-12">
        <div className="sticky top-0 h-screen flex flex-col justify-center">
          <div className="flex items-center gap-3 mb-8">
            <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-brand-sky to-brand-green" />
            <div className="text-2xl font-extrabold text-slate-900 dark:text-white">EduFunds</div>
          </div>
          <h1 className="text-5xl font-extrabold mb-6 text-slate-900 dark:text-white">
            Bildungsfinanzierung <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-sky to-brand-green">leicht gemacht</span>
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-300 max-w-lg mb-10">
            KI-gestützte Antragstellung, transparente Fördermittelübersicht und kollaborative Prozesse – für moderne Grundschulen.
          </p>
          <div className="grid grid-cols-3 gap-4">
            <div className="card">
              <Sparkles className="h-8 w-8 text-brand-sky mb-2" />
              <div className="text-3xl font-extrabold text-slate-900 dark:text-white">2x</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">schnellere Anträge</div>
            </div>
            <div className="card">
              <TrendingUp className="h-8 w-8 text-brand-green mb-2" />
              <div className="text-3xl font-extrabold text-slate-900 dark:text-white">99,9%</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Uptime</div>
            </div>
            <div className="card">
              <Users className="h-8 w-8 text-brand-navy mb-2" />
              <div className="text-3xl font-extrabold text-slate-900 dark:text-white">DSGVO</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">konform</div>
            </div>
          </div>
        </div>
      </div>
      <div className="flex items-center justify-center p-8">
        <div className="card w-full max-w-md p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-brand-sky to-brand-green" />
            <div>
              <div className="text-xl font-extrabold text-slate-900 dark:text-white">EduFunds</div>
              <div className="text-slate-500 dark:text-slate-400 text-sm">Bitte anmelden</div>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-700 dark:text-red-400 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-semibold mb-1">Login fehlgeschlagen</div>
                <div className="text-sm">{error}</div>
              </div>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label
                htmlFor="login-email"
                className="block text-sm font-semibold mb-2 text-slate-600 dark:text-slate-300"
              >
                E-Mail
              </label>
              <input
                id="login-email"
                className="input"
                type="email"
                placeholder="name@schule.de"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                required
              />
            </div>
            <div>
              <label
                htmlFor="login-password"
                className="block text-sm font-semibold mb-2 text-slate-600 dark:text-slate-300"
              >
                Passwort
              </label>
              <input
                id="login-password"
                className="input"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                required
              />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Wird angemeldet…</span>
                </>
              ) : (
                <span>Anmelden</span>
              )}
            </button>
          </form>

          <div className="mt-6 p-4 rounded-2xl bg-brand-sky/10 border border-brand-sky/20">
            <div className="text-sm font-semibold mb-2 text-brand-navy dark:text-brand-sky">Testzugang</div>
            <div className="font-mono text-sm text-slate-700 dark:text-slate-300 space-y-1">
              <div>admin@gs-musterberg.de</div>
              <div>test1234</div>
            </div>
          </div>

          <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
            Mit Ihrer Schul-E-Mail anmelden. Support: support@edufunds.de
          </p>
        </div>
      </div>
    </div>
  )
}
