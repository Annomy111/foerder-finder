import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import useAuthStore from '@/store/authStore'
import Layout from '@/components/Layout'

// Lazy pages
const WelcomeScreen = lazy(() => import('@/components/WelcomeScreen'))
const LoginPage = lazy(() => import('@/pages/LoginPage'))
const DashboardPage = lazy(() => import('@/pages/DashboardPage'))
const FundingListPage = lazy(() => import('@/pages/FundingListPage'))
const FundingDetailPage = lazy(() => import('@/pages/FundingDetailPage'))
const ApplicationsPage = lazy(() => import('@/pages/ApplicationsPage'))
const ApplicationDetailPage = lazy(() => import('@/pages/ApplicationDetailPage'))
const SearchPage = lazy(() => import('@/pages/SearchPage'))

function PageLoader() {
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-gradient-to-br from-brand-navy/95 via-brand-teal/90 to-brand-green/90">
      <div className="text-center">
        <div className="relative mx-auto mb-4 h-14 w-14">
          <div className="absolute inset-0 animate-spin rounded-full border-4 border-white/20 border-t-white"></div>
          <div className="absolute inset-2 rounded-full bg-white/20 backdrop-blur" />
        </div>
        <p className="text-white text-lg font-semibold tracking-wide">Lädt…</p>
      </div>
    </div>
  )
}

function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return (
    <Layout>
      <AnimatePresence mode="wait">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
          className="min-h-[calc(100vh-64px)]"
        >
          {children}
        </motion.div>
      </AnimatePresence>
    </Layout>
  )
}

function HomeRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return isAuthenticated ? (
    <Navigate to="/dashboard" replace />
  ) : (
    <WelcomeScreen />
  )
}

export default function App() {
  const location = useLocation()
  return (
    <Suspense fallback={<PageLoader />}>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          {/* Public */}
          <Route path="/" element={<HomeRoute />} />
          <Route path="/login" element={<LoginPage />} />

          {/* Protected */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/search"
            element={
              <ProtectedRoute>
                <SearchPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/funding"
            element={
              <ProtectedRoute>
                <FundingListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/funding/:fundingId"
            element={
              <ProtectedRoute>
                <FundingDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/applications"
            element={
              <ProtectedRoute>
                <ApplicationsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/applications/:applicationId"
            element={
              <ProtectedRoute>
                <ApplicationDetailPage />
              </ProtectedRoute>
            }
          />

          {/* 404 - Redirect to home (Welcome or Dashboard) */}
          <Route path="*" element={<HomeRoute />} />
        </Routes>
      </AnimatePresence>
    </Suspense>
  )
}
