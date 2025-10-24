import { Routes, Route, Navigate } from 'react-router-dom'
import useAuthStore from '@/store/authStore'

// Pages
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import FundingListPage from '@/pages/FundingListPage'
import FundingDetailPage from '@/pages/FundingDetailPage'
import ApplicationsPage from '@/pages/ApplicationsPage'
import ApplicationDetailPage from '@/pages/ApplicationDetailPage'

// Components
import Layout from '@/components/Layout'

/**
 * Protected Route Wrapper
 */
function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Layout>{children}</Layout>
}

/**
 * Main App Component
 */
function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protected Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardPage />
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

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
