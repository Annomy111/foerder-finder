import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { applicationsAPI, fundingAPI } from '@/services/api'
import { FileText, TrendingUp, Clock, ArrowRight, Calendar, Building2 } from 'lucide-react'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'

/**
 * Dashboard Page - Übersicht mit modernem Design
 */
function DashboardPage() {
  const [stats, setStats] = useState({
    totalApplications: 0,
    activeFundings: 0,
    recentApplications: [],
    recentFundings: [],
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [applications, fundings] = await Promise.all([
        applicationsAPI.list(),
        fundingAPI.list({ limit: 5 }),
      ])

      setStats({
        totalApplications: applications.length,
        activeFundings: fundings.length,
        recentApplications: applications.slice(0, 5),
        recentFundings: fundings,
      })
    } catch (error) {
      console.error('Fehler beim Laden der Dashboard-Daten:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <LoadingSpinner text="Dashboard wird geladen..." />
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold gradient-text mb-2">Dashboard</h1>
        <p className="text-gray-600">Willkommen zurück! Hier ist Ihre Übersicht.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          icon={<FileText className="text-primary-600" size={32} />}
          label="Meine Anträge"
          value={stats.totalApplications}
          link="/applications"
          gradient="from-primary-500 to-primary-600"
        />
        <StatCard
          icon={<TrendingUp className="text-green-600" size={32} />}
          label="Aktive Fördermittel"
          value={stats.activeFundings}
          link="/funding"
          gradient="from-green-500 to-emerald-600"
        />
        <StatCard
          icon={<Clock className="text-orange-600" size={32} />}
          label="In Bearbeitung"
          value={stats.recentApplications.filter((a) => a.status === 'in_bearbeitung').length}
          gradient="from-orange-500 to-amber-600"
        />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Applications */}
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Letzte Anträge</h2>
            <Link to="/applications" className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center space-x-1">
              <span>Alle anzeigen</span>
              <ArrowRight size={16} />
            </Link>
          </div>

          {stats.recentApplications.length === 0 ? (
            <EmptyState
              icon={FileText}
              title="Noch keine Anträge"
              description="Erstellen Sie Ihren ersten Förderantrag"
              action={
                <Link to="/funding" className="btn-primary inline-block">
                  Fördermittel entdecken
                </Link>
              }
            />
          ) : (
            <div className="space-y-3">
              {stats.recentApplications.map((app) => (
                <ApplicationCard key={app.application_id} app={app} />
              ))}
            </div>
          )}
        </div>

        {/* Recent Fundings */}
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Neue Fördermittel</h2>
            <Link to="/funding" className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center space-x-1">
              <span>Alle anzeigen</span>
              <ArrowRight size={16} />
            </Link>
          </div>

          {stats.recentFundings.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>Keine Fördermittel verfügbar</p>
            </div>
          ) : (
            <div className="space-y-3">
              {stats.recentFundings.map((funding) => (
                <FundingCard key={funding.funding_id} funding={funding} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/**
 * Stat Card Component mit Gradient
 */
function StatCard({ icon, label, value, link, gradient }) {
  const content = (
    <div className="card-interactive group">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className={`p-3 bg-gradient-to-br ${gradient} rounded-xl text-white shadow-lg`}>
            {icon}
          </div>
          <div>
            <p className="text-sm text-gray-600 font-medium">{label}</p>
            <p className="text-3xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
              {value}
            </p>
          </div>
        </div>
        <ArrowRight className="text-gray-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all" size={24} />
      </div>
    </div>
  )

  return link ? <Link to={link}>{content}</Link> : content
}

/**
 * Application Card Component
 */
function ApplicationCard({ app }) {
  return (
    <Link
      to={`/applications/${app.application_id}`}
      className="block p-4 border-2 border-gray-100 rounded-xl hover:border-primary-300 hover:shadow-md transition-all duration-200 group"
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="font-medium text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-1">
            {app.title}
          </h3>
          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
            <span className="flex items-center space-x-1">
              <Calendar size={12} />
              <span>{new Date(app.created_at).toLocaleDateString('de-DE')}</span>
            </span>
          </div>
        </div>
        <StatusBadge status={app.status} />
      </div>
    </Link>
  )
}

/**
 * Funding Card Component (Klein)
 */
function FundingCard({ funding }) {
  return (
    <Link
      to={`/funding/${funding.funding_id}`}
      className="block p-4 border-2 border-gray-100 rounded-xl hover:border-primary-300 hover:shadow-md transition-all duration-200 group"
    >
      <h3 className="font-medium text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-2 mb-2">
        {funding.title}
      </h3>
      <div className="flex items-center justify-between text-xs">
        <span className="flex items-center space-x-1 text-gray-500">
          <Building2 size={12} />
          <span>{funding.provider || 'Unbekannt'}</span>
        </span>
        {funding.funding_area && (
          <span className="badge badge-primary">{funding.funding_area}</span>
        )}
      </div>
    </Link>
  )
}

/**
 * Status Badge Component
 */
function StatusBadge({ status }) {
  const variants = {
    entwurf: 'bg-gray-100 text-gray-800 border-gray-200',
    in_bearbeitung: 'bg-blue-100 text-blue-800 border-blue-200',
    eingereicht: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    genehmigt: 'bg-green-100 text-green-800 border-green-200',
    abgelehnt: 'bg-red-100 text-red-800 border-red-200',
  }

  const labels = {
    entwurf: 'Entwurf',
    in_bearbeitung: 'In Bearbeitung',
    eingereicht: 'Eingereicht',
    genehmigt: 'Genehmigt',
    abgelehnt: 'Abgelehnt',
  }

  return (
    <span className={`badge border ${variants[status]}`}>
      {labels[status]}
    </span>
  )
}

export default DashboardPage
