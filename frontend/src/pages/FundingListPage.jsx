import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fundingAPI } from '@/services/api'
import { Calendar, MapPin, Building2, Filter, X, Euro } from 'lucide-react'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'

/**
 * Funding List Page - Alle Fördermittel mit Filter
 */
function FundingListPage() {
  const [fundings, setFundings] = useState([])
  const [loading, setLoading] = useState(true)
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState({
    region: '',
    funding_area: '',
    provider: '',
  })

  useEffect(() => {
    loadFundings()
  }, [filters])

  const loadFundings = async () => {
    try {
      const activeFilters = Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v !== '')
      )
      const data = await fundingAPI.list(activeFilters)
      setFundings(data)
    } catch (error) {
      console.error('Fehler beim Laden der Fördermittel:', error)
    } finally {
      setLoading(false)
    }
  }

  const clearFilters = () => {
    setFilters({ region: '', funding_area: '', provider: '' })
  }

  const hasActiveFilters = Object.values(filters).some((v) => v !== '')

  if (loading) {
    return <LoadingSpinner text="Fördermittel werden geladen..." />
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold gradient-text mb-2">Fördermittel</h1>
          <p className="text-gray-600">
            {fundings.length} aktive Förderprogramme verfügbar
          </p>
        </div>

        {/* Filter Toggle Button */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`btn-${showFilters ? 'primary' : 'secondary'} flex items-center space-x-2`}
        >
          <Filter size={20} />
          <span>Filter {hasActiveFilters && `(${Object.values(filters).filter(v => v).length})`}</span>
        </button>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="card animate-fade-in">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-gray-900">Filter</h3>
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center space-x-1"
              >
                <X size={16} />
                <span>Zurücksetzen</span>
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Region Filter */}
            <div>
              <label className="label">Region</label>
              <select
                className="input"
                value={filters.region}
                onChange={(e) => setFilters({ ...filters, region: e.target.value })}
              >
                <option value="">Alle Regionen</option>
                <option value="Bundesweit">Bundesweit</option>
                <option value="Berlin">Berlin</option>
                <option value="Brandenburg">Brandenburg</option>
                <option value="Sachsen">Sachsen</option>
              </select>
            </div>

            {/* Funding Area Filter */}
            <div>
              <label className="label">Förderbereich</label>
              <select
                className="input"
                value={filters.funding_area}
                onChange={(e) => setFilters({ ...filters, funding_area: e.target.value })}
              >
                <option value="">Alle Bereiche</option>
                <option value="Digitalisierung">Digitalisierung</option>
                <option value="Sport">Sport</option>
                <option value="MINT">MINT</option>
                <option value="Inklusion">Inklusion</option>
                <option value="Kunst">Kunst</option>
              </select>
            </div>

            {/* Provider Filter */}
            <div>
              <label className="label">Fördergeber</label>
              <select
                className="input"
                value={filters.provider}
                onChange={(e) => setFilters({ ...filters, provider: e.target.value })}
              >
                <option value="">Alle Fördergeber</option>
                <option value="BMBF">BMBF</option>
                <option value="Land Brandenburg">Land Brandenburg</option>
                <option value="DigitalPakt Schule">DigitalPakt Schule</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Funding Cards Grid */}
      {fundings.length === 0 ? (
        <EmptyState
          title="Keine Fördermittel gefunden"
          description="Passen Sie Ihre Filter an oder schauen Sie später wieder vorbei."
          action={
            hasActiveFilters && (
              <button onClick={clearFilters} className="btn-primary">
                Filter zurücksetzen
              </button>
            )
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {fundings.map((funding) => (
            <FundingCard key={funding.funding_id} funding={funding} />
          ))}
        </div>
      )}
    </div>
  )
}

/**
 * Funding Card Component
 */
function FundingCard({ funding }) {
  const daysUntilDeadline = funding.deadline
    ? Math.ceil((new Date(funding.deadline) - new Date()) / (1000 * 60 * 60 * 24))
    : null

  return (
    <Link
      to={`/funding/${funding.funding_id}`}
      className="card-interactive group"
    >
      {/* Header */}
      <div className="mb-4">
        <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors mb-2 line-clamp-2">
          {funding.title}
        </h3>
      </div>

      {/* Meta Info */}
      <div className="space-y-2 text-sm text-gray-600 mb-4">
        <div className="flex items-center space-x-2">
          <Building2 size={16} className="flex-shrink-0" />
          <span className="truncate">{funding.provider || 'Keine Angabe'}</span>
        </div>

        <div className="flex items-center space-x-2">
          <MapPin size={16} className="flex-shrink-0" />
          <span>{funding.region || 'Bundesweit'}</span>
        </div>

        {funding.deadline && (
          <div className="flex items-center space-x-2">
            <Calendar size={16} className="flex-shrink-0" />
            <div className="flex items-center space-x-2">
              <span>{new Date(funding.deadline).toLocaleDateString('de-DE')}</span>
              {daysUntilDeadline !== null && (
                <span className={`text-xs font-medium ${
                  daysUntilDeadline < 7 ? 'text-red-600' :
                  daysUntilDeadline < 30 ? 'text-orange-600' : 'text-green-600'
                }`}>
                  ({daysUntilDeadline} Tage)
                </span>
              )}
            </div>
          </div>
        )}

        {(funding.min_funding_amount || funding.max_funding_amount) && (
          <div className="flex items-center space-x-2">
            <Euro size={16} className="flex-shrink-0" />
            <span>
              {funding.min_funding_amount && `ab ${funding.min_funding_amount.toLocaleString('de-DE')}€`}
              {funding.max_funding_amount && ` bis ${funding.max_funding_amount.toLocaleString('de-DE')}€`}
            </span>
          </div>
        )}
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-2">
        {funding.funding_area && (
          <span className="badge badge-primary">
            {funding.funding_area}
          </span>
        )}
        {funding.tags && funding.tags.slice(0, 2).map((tag, i) => (
          <span key={i} className="badge bg-gray-100 text-gray-700 border-gray-200">
            {tag}
          </span>
        ))}
      </div>
    </Link>
  )
}

export default FundingListPage
