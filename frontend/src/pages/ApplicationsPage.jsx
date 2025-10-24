import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { applicationsAPI } from '@/services/api'
import { FileText, Calendar, TrendingUp, Plus } from 'lucide-react'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'

function ApplicationsPage() {
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, entwurf, eingereicht, etc.

  useEffect(() => {
    loadApplications()
  }, [])

  const loadApplications = async () => {
    try {
      const data = await applicationsAPI.list()
      setApplications(data)
    } catch (error) {
      console.error('Fehler:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredApplications = applications.filter((app) =>
    filter === 'all' ? true : app.status === filter
  )

  const stats = {
    total: applications.length,
    entwurf: applications.filter((a) => a.status === 'entwurf').length,
    eingereicht: applications.filter((a) => a.status === 'eingereicht').length,
    genehmigt: applications.filter((a) => a.status === 'genehmigt').length,
  }

  if (loading) {
    return <LoadingSpinner text="Anträge werden geladen..." />
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold gradient-text mb-2">Meine Anträge</h1>
          <p className="text-gray-600">{stats.total} Anträge insgesamt</p>
        </div>

        <Link to="/funding" className="btn-primary flex items-center space-x-2">
          <Plus size={20} />
          <span>Neuer Antrag</span>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatBox
          label="Entwürfe"
          value={stats.entwurf}
          color="gray"
          active={filter === 'entwurf'}
          onClick={() => setFilter(filter === 'entwurf' ? 'all' : 'entwurf')}
        />
        <StatBox
          label="Eingereicht"
          value={stats.eingereicht}
          color="blue"
          active={filter === 'eingereicht'}
          onClick={() => setFilter(filter === 'eingereicht' ? 'all' : 'eingereicht')}
        />
        <StatBox
          label="Genehmigt"
          value={stats.genehmigt}
          color="green"
          active={filter === 'genehmigt'}
          onClick={() => setFilter(filter === 'genehmigt' ? 'all' : 'genehmigt')}
        />
        <StatBox
          label="Gesamt"
          value={stats.total}
          color="primary"
          active={filter === 'all'}
          onClick={() => setFilter('all')}
        />
      </div>

      {/* Applications List */}
      {filteredApplications.length === 0 ? (
        <EmptyState
          icon={FileText}
          title={filter === 'all' ? 'Noch keine Anträge' : `Keine Anträge (${filter})`}
          description="Erstellen Sie einen neuen Antrag für eine Fördermittel-Ausschreibung."
          action={
            <Link to="/funding" className="btn-primary inline-flex items-center space-x-2">
              <Plus size={20} />
              <span>Fördermittel entdecken</span>
            </Link>
          }
        />
      ) : (
        <div className="space-y-4">
          {filteredApplications.map((app) => (
            <ApplicationCard key={app.application_id} app={app} />
          ))}
        </div>
      )}
    </div>
  )
}

/**
 * Stat Box Component
 */
function StatBox({ label, value, color, active, onClick }) {
  const colors = {
    gray: 'from-gray-500 to-gray-600',
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-emerald-600',
    primary: 'from-primary-500 to-primary-600',
  }

  return (
    <button
      onClick={onClick}
      className={`card text-left transition-all duration-200 ${
        active ? 'ring-2 ring-primary-500 shadow-xl' : 'hover:shadow-xl'
      }`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 font-medium mb-1">{label}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-2 bg-gradient-to-br ${colors[color]} rounded-lg`}>
          <TrendingUp className="text-white" size={24} />
        </div>
      </div>
    </button>
  )
}

/**
 * Application Card Component
 */
function ApplicationCard({ app }) {
  const statusColors = {
    entwurf: 'border-gray-300',
    in_bearbeitung: 'border-blue-300',
    eingereicht: 'border-yellow-300',
    genehmigt: 'border-green-300',
    abgelehnt: 'border-red-300',
  }

  return (
    <Link
      to={`/applications/${app.application_id}`}
      className={`card-interactive border-l-4 ${statusColors[app.status]}`}
    >
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex-1">
          <h3 className="font-semibold text-lg text-gray-900 mb-2">{app.title}</h3>

          {app.projektbeschreibung && (
            <p className="text-sm text-gray-600 line-clamp-2 mb-3">
              {app.projektbeschreibung}
            </p>
          )}

          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center space-x-1">
              <Calendar size={14} />
              <span>Erstellt: {new Date(app.created_at).toLocaleDateString('de-DE')}</span>
            </span>

            {app.budget_total && (
              <span className="flex items-center space-x-1">
                <span>Budget:</span>
                <span className="font-medium text-gray-900">
                  {app.budget_total.toLocaleString('de-DE')}€
                </span>
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <StatusBadge status={app.status} />
        </div>
      </div>
    </Link>
  )
}

/**
 * Status Badge Component
 */
function StatusBadge({ status }) {
  const variants = {
    entwurf: 'badge bg-gray-100 text-gray-800 border-gray-200',
    in_bearbeitung: 'badge bg-blue-100 text-blue-800 border-blue-200',
    eingereicht: 'badge bg-yellow-100 text-yellow-800 border-yellow-200',
    genehmigt: 'badge bg-green-100 text-green-800 border-green-200',
    abgelehnt: 'badge bg-red-100 text-red-800 border-red-200',
  }

  const labels = {
    entwurf: 'Entwurf',
    in_bearbeitung: 'In Bearbeitung',
    eingereicht: 'Eingereicht',
    genehmigt: 'Genehmigt',
    abgelehnt: 'Abgelehnt',
  }

  return <span className={`${variants[status]} border text-sm font-semibold px-4 py-2`}>{labels[status]}</span>
}

export default ApplicationsPage
