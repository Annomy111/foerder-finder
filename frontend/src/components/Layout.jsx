import { Link, useNavigate, useLocation } from 'react-router-dom'
import useAuthStore from '@/store/authStore'
import { Home, FileText, FileSearch, LogOut, Sparkles } from 'lucide-react'

/**
 * Main Layout Component mit modernerer Navigation
 */
function Layout({ children }) {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header with Gradient */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-primary-500 to-indigo-600 rounded-xl">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold gradient-text">
                  Förder-Finder
                </h1>
                <p className="text-xs text-gray-500">KI-gestützte Antragstellung</p>
              </div>
            </div>

            <div className="flex items-center space-x-6">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {user?.first_name || user?.email?.split('@')[0]}
                </p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="btn-ghost flex items-center space-x-2"
              >
                <LogOut size={18} />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white/60 backdrop-blur-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1">
            <NavLink
              to="/"
              icon={<Home size={20} />}
              label="Dashboard"
              isActive={location.pathname === '/'}
            />
            <NavLink
              to="/funding"
              icon={<FileSearch size={20} />}
              label="Fördermittel"
              isActive={location.pathname.startsWith('/funding')}
            />
            <NavLink
              to="/applications"
              icon={<FileText size={20} />}
              label="Meine Anträge"
              isActive={location.pathname.startsWith('/applications')}
            />
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white/60 backdrop-blur-sm border-t border-gray-100 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row justify-between items-center space-y-2 sm:space-y-0">
            <p className="text-sm text-gray-600">
              © 2024 Förder-Finder Grundschule
            </p>
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              <span>Powered by</span>
              <span className="font-semibold gradient-text">DeepSeek AI</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

/**
 * Navigation Link Component mit Active State
 */
function NavLink({ to, icon, label, isActive }) {
  return (
    <Link
      to={to}
      className={`flex items-center space-x-2 px-4 py-3 rounded-t-xl transition-all duration-200 ${
        isActive
          ? 'bg-white text-primary-600 shadow-sm border-b-2 border-primary-600 font-semibold'
          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
      }`}
    >
      {icon}
      <span>{label}</span>
    </Link>
  )
}

export default Layout
