import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '@/store/authStore'
import { authAPI } from '@/services/api'
import { Sparkles, AlertCircle, Loader2 } from 'lucide-react'

/**
 * Login Page mit modernem Design
 */
function LoginPage() {
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const response = await authAPI.login(email, password)

      login(
        {
          user_id: response.user_id,
          school_id: response.school_id,
          email: email,
          role: response.role,
        },
        response.access_token
      )

      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login fehlgeschlagen')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 via-indigo-600 to-purple-700 py-12 px-4 sm:px-6 lg:px-8">
      {/* Floating Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-white/10 rounded-full blur-3xl"></div>
      </div>

      <div className="max-w-md w-full space-y-8 relative z-10">
        {/* Logo & Header */}
        <div className="text-center animate-fade-in">
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-white rounded-2xl shadow-2xl">
              <Sparkles className="w-12 h-12 text-primary-600" />
            </div>
          </div>
          <h2 className="text-4xl font-extrabold text-white mb-2">
            Förder-Finder
          </h2>
          <p className="text-lg text-white/80">
            KI-gestützte Fördermittel-Antragstellung
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-8 animate-fade-in">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border-2 border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-start space-x-3 animate-fade-in">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            {/* Email Input */}
            <div>
              <label htmlFor="email" className="label">
                E-Mail Adresse
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="input"
                placeholder="ihre.email@schule.de"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
              />
            </div>

            {/* Password Input */}
            <div>
              <label htmlFor="password" className="label">
                Passwort
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Wird angemeldet...</span>
                </>
              ) : (
                <span>Anmelden</span>
              )}
            </button>
          </form>

          {/* Demo Account Info */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <p className="text-xs font-semibold text-blue-900 mb-2">
                Demo-Account zum Testen:
              </p>
              <div className="space-y-1 text-xs text-blue-700 font-mono">
                <p>admin@gs-musterberg.de</p>
                <p>test1234</p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-white/80 animate-fade-in">
          <p>Powered by DeepSeek AI</p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
