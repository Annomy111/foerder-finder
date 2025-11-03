import { useEffect, useMemo, useState, useTransition, useDeferredValue } from 'react'
import { Link } from 'react-router-dom'
import { fundingAPI } from '@/services/api'
import {
  MapPin,
  Building2,
  Filter,
  X,
  Euro,
  Clock,
  TrendingUp,
  Award,
  Info,
  Sparkles,
  Compass,
  Layers,
  Globe2,
  ArrowRight,
} from 'lucide-react'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'
import InfoBox from '@/components/ui/InfoBox'
import DismissibleBanner from '@/components/ui/DismissibleBanner'
import FundingCard from '@/components/FundingCard'


/**
 * Funding List Page - Alle Fördermittel mit Filter
 */
function FundingListPage() {
  const [fundings, setFundings] = useState([])
  const [loading, setLoading] = useState(true)
  const [showFilters, setShowFilters] = useState(false)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({
    region: '',
    funding_area: '',
    provider: '',
  })
  const [isPending, startTransition] = useTransition()
  const deferredFundings = useDeferredValue(fundings)

  useEffect(() => {
    let isMounted = true

    const fetchFundings = async () => {
      try {
        setLoading(true)
        setError(null)
        const activeFilters = Object.fromEntries(
          Object.entries(filters).filter(([, value]) => value !== '')
        )
        const data = await fundingAPI.list(activeFilters)
        if (isMounted) {
          setFundings(data)
        }
      } catch (error) {
        if (isMounted) {
          console.error('Fehler beim Laden der Fördermittel:', error)
          setError('Fehler beim Laden der Fördermittel. Bitte versuchen Sie es erneut.')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchFundings()

    return () => {
      isMounted = false
    }
  }, [filters])

  const clearFilters = () => {
    startTransition(() => {
      setFilters({ region: '', funding_area: '', provider: '' })
    })
  }

  const updateFilter = (key, value) => {
    startTransition(() => {
      setFilters({ ...filters, [key]: value })
    })
  }

  const hasActiveFilters = Object.values(filters).some((v) => v !== '')
  const activeFilterCount = Object.values(filters).filter(Boolean).length

  const landscapeBadges = [
    { label: 'EU', desc: 'Mobilität & Innovation', icon: Globe2 },
    { label: 'Bund', desc: 'Startchancen & DigitalPakt', icon: Building2 },
    { label: 'Länder', desc: 'KMK-Schwerpunkte', icon: Layers },
    { label: 'Stiftungen', desc: 'Agile Projektmittel', icon: Sparkles },
  ]

  const { totalFunding, urgentDeadlines } = useMemo(() => {
    const total = deferredFundings.reduce((sum, item) => sum + (item.max_funding_amount || 0), 0)
    const urgent = deferredFundings.filter((item) => {
      if (!item.deadline) return false
      const days = Math.ceil((new Date(item.deadline) - new Date()) / (1000 * 60 * 60 * 24))
      return days < 30
    }).length

    return { totalFunding: total, urgentDeadlines: urgent }
  }, [deferredFundings])

  const isStale = fundings !== deferredFundings

  if (loading) {
    return <LoadingSpinner text="Fördermittel werden geladen..." />
  }

  return (
    <div className="space-y-10">
      <section className="hero-shell">
        <div className="grid gap-8 lg:grid-cols-[1.25fr_1fr]">
          <div className="space-y-6">
            <span className="chip border-transparent bg-brand-navy/10 text-brand-navy">
              <Sparkles size={16} /> Smart Funding Navigator
            </span>
            <div className="space-y-3">
              <h1 className="text-3xl font-semibold text-brand-navy md:text-4xl">
                Fördermittel-Intelligence für Grundschulen
              </h1>
              <p className="max-w-2xl text-base text-slate-600 md:text-lg">
                Kuratierte Programme aus EU, Bund, Ländern und Stiftungen – priorisiert nach Aufwand, Wirkung und Mandantenfit. Modular aufgebaut für schnelle Entscheidungen.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 text-sm text-slate-600">
              <span className="chip">{deferredFundings.length} Programme aktiv</span>
              <span className="chip">{urgentDeadlines} Deadlines &lt; 30 Tage</span>
              <span className="chip">{totalFunding.toLocaleString('de-DE')} € Volumen</span>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <button onClick={() => setShowFilters(true)} className="btn-primary">
                <Filter size={18} /> Filter aktivieren
              </button>
              {hasActiveFilters && (
                <button onClick={clearFilters} className="btn-ghost text-sm font-semibold text-brand-navy">
                  Zurücksetzen
                </button>
              )}
              <Link to="/search" className="btn-secondary">
                KI-Suche starten
              </Link>
            </div>
          </div>

          <div className="rounded-3xl border border-white/70 bg-white/95 p-6 shadow-md">
            <p className="section-title text-brand-navy/70">Landscape Snapshot</p>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              {landscapeBadges.map(({ label, desc, icon: Icon }) => (
                <div key={label} className="rounded-2xl border border-slate-200/70 bg-white/90 p-3 shadow-sm">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-brand-navy">
                    <Icon size={16} /> {label}
                  </div>
                  <p className="mt-2 text-xs text-slate-500">{desc}</p>
                </div>
              ))}
            </div>
            <div className="mt-6 grid grid-cols-2 gap-3">
              <HeroSummaryTile
                icon={Compass}
                label="Programme im Fokus"
                value={deferredFundings.length}
                caption={hasActiveFilters ? 'Gefiltert nach Ihren Kriterien' : 'Alle öffentlichen Programme'}
              />
              <HeroSummaryTile
                icon={Clock}
                label="Fristen &lt; 30 Tage"
                value={urgentDeadlines}
                caption="Priorisieren für schnelle Wirkung"
              />
              <HeroSummaryTile
                icon={Euro}
                label="Gesamtvolumen"
                value={`${totalFunding.toLocaleString('de-DE')} €`}
                caption="Summierte Fördersumme"
              />
              <HeroSummaryTile
                icon={Filter}
                label="Filter aktiv"
                value={hasActiveFilters ? activeFilterCount : 0}
                caption={hasActiveFilters ? 'Kontextualisierte Treffer' : 'Keine Filter gesetzt'}
              />
            </div>
          </div>
        </div>
      </section>

      {error && (
        <InfoBox variant="danger" title="Fehler beim Laden">
          {error}
        </InfoBox>
      )}

      <DismissibleBanner id="funding-tour">
        {({ close }) => (
          <div className="glass-surface relative overflow-hidden rounded-3xl px-6 py-6 sm:px-8">
            <div className="absolute -right-16 top-1/2 hidden h-36 w-36 -translate-y-1/2 rounded-full bg-brand-green/25 blur-3xl lg:block" />
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div className="flex items-start gap-3 text-brand-navy">
                <span className="mt-1 inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-navy/10">
                  <Info size={20} />
                </span>
                <div className="space-y-1">
                  <h2 className="text-lg font-semibold">So nutzen Sie EduFunds ideal</h2>
                  <p className="text-sm text-slate-600">
                    Aktivieren Sie Filter, markieren Sie Favoriten und starten Sie direkt die KI-gestützte Antragserstellung aus jeder Detailansicht.
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <Link to="/applications" className="btn-secondary text-sm">
                  Aktuelle Anträge öffnen
                </Link>
                <button onClick={close} className="btn-ghost text-xs uppercase tracking-wide text-slate-500">
                  Ausblenden
                </button>
              </div>
            </div>
          </div>
        )}
      </DismissibleBanner>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <StatCard icon={Award} label="Verfügbare Programme" value={deferredFundings.length} color="text-brand-navy" />
        <StatCard icon={TrendingUp} label="Gesamtvolumen" value={`${totalFunding.toLocaleString('de-DE')} €`} color="text-emerald-600" />
        <StatCard icon={Clock} label="Fristen < 30 Tage" value={urgentDeadlines} color="text-amber-600" />
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="card animate-fade-in">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <h3 className="text-base font-semibold text-brand-navy">Filter</h3>
              <span className="badge-soft text-xs">
                {hasActiveFilters ? `${activeFilterCount} aktiv` : 'Keine aktiv'}
              </span>
              {isPending && (
                <span className="flex items-center gap-1 text-xs text-brand-navy/60">
                  <svg className="h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Wird aktualisiert...
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 text-xs">
              <button
                onClick={() => setShowFilters(false)}
                className="btn-ghost text-xs font-semibold uppercase tracking-wide text-slate-500"
              >
                Schließen
              </button>
            </div>
            <InfoBox variant="info" className="w-full border-dashed sm:w-auto">
              Präzisieren Sie Ihre Suche nach Regionen, Bereichen und Fördergebern. Wir zeigen nur Programme mit echten Erfolgschancen.
            </InfoBox>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <FilterSelect
              label="Region"
              value={filters.region}
              onChange={(value) => updateFilter('region', value)}
              options={[
                { label: 'Alle Regionen', value: '' },
                { label: 'Bundesweit', value: 'Bundesweit' },
                { label: 'Baden-Württemberg', value: 'Baden-Württemberg' },
                { label: 'Bayern', value: 'Bayern' },
                { label: 'Berlin', value: 'Berlin' },
                { label: 'Brandenburg', value: 'Brandenburg' },
                { label: 'Bremen', value: 'Bremen' },
                { label: 'Hamburg', value: 'Hamburg' },
                { label: 'Hessen', value: 'Hessen' },
                { label: 'Mecklenburg-Vorpommern', value: 'Mecklenburg-Vorpommern' },
                { label: 'Niedersachsen', value: 'Niedersachsen' },
                { label: 'Nordrhein-Westfalen', value: 'Nordrhein-Westfalen' },
                { label: 'Rheinland-Pfalz', value: 'Rheinland-Pfalz' },
                { label: 'Saarland', value: 'Saarland' },
                { label: 'Sachsen', value: 'Sachsen' },
                { label: 'Sachsen-Anhalt', value: 'Sachsen-Anhalt' },
                { label: 'Schleswig-Holstein', value: 'Schleswig-Holstein' },
                { label: 'Thüringen', value: 'Thüringen' },
              ]}
              icon={MapPin}
            />

            <FilterSelect
              label="Förderbereich"
              value={filters.funding_area}
              onChange={(value) => updateFilter('funding_area', value)}
              options={[
                { label: 'Alle Bereiche', value: '' },
                { label: 'Digitalisierung', value: 'Digitalisierung' },
                { label: 'Sport', value: 'Sport' },
                { label: 'MINT', value: 'MINT' },
                { label: 'Inklusion', value: 'Inklusion' },
                { label: 'Kunst', value: 'Kunst' },
              ]}
              icon={Sparkles}
            />

            <FilterSelect
              label="Fördergeber"
              value={filters.provider}
              onChange={(value) => updateFilter('provider', value)}
              options={[
                { label: 'Alle Fördergeber', value: '' },
                { label: 'BMBF', value: 'BMBF' },
                { label: 'Land Brandenburg', value: 'Land Brandenburg' },
                { label: 'DigitalPakt Schule', value: 'DigitalPakt Schule' },
              ]}
              icon={Building2}
            />
          </div>

          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-brand-navy/80"
            >
              <X size={16} /> Filter zurücksetzen
            </button>
          )}
        </div>
      )}

      {/* Funding Cards Grid */}
      {deferredFundings.length === 0 ? (
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
        <div
          className={`grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3 transition-opacity duration-200 ${
            isPending || isStale ? 'opacity-60' : 'opacity-100'
          }`}
        >
          {deferredFundings.map((funding, index) => {
            const key =
              funding.funding_id ||
              funding.id ||
              funding.uuid ||
              funding.slug ||
              `funding-${index}`
            return <FundingCard key={key} funding={funding} />
          })}
        </div>
      )}
    </div>
  )
}

function HeroSummaryTile({ icon: IconComponent, label, value, caption }) {
  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white/90 p-4 shadow-sm">
      <div className="flex items-center gap-2">
        <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-brand-navy/10 text-brand-navy">
          <IconComponent size={16} />
        </span>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      </div>
      <p className="mt-3 text-lg font-semibold text-brand-navy">{value}</p>
      <p className="text-xs text-slate-500">{caption}</p>
    </div>
  )
}

function StatCard({ icon: IconComponent, label, value, color }) {
  return (
    <div className="rounded-3xl border border-slate-200/80 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-navy/10 text-brand-navy">
          <IconComponent size={22} className={color} />
        </span>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
          <p className="text-xl font-semibold text-brand-navy">{value}</p>
        </div>
      </div>
    </div>
  )
}

function FilterSelect({ label, value, onChange, options, icon: IconComponent }) {
  return (
    <label className="flex flex-col gap-2">
      <span className="label">{label}</span>
    <div className="flex items-center gap-2 rounded-2xl border border-slate-200/80 bg-white px-4 py-2 shadow-sm">
      {IconComponent && <IconComponent size={18} className="text-brand-navy/50" />}
      <select
        className="w-full border-none bg-transparent text-sm font-medium text-brand-navy focus:outline-none"
          value={value}
          onChange={(event) => onChange(event.target.value)}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value} className="text-slate-700">
              {option.label}
            </option>
          ))}
        </select>
      </div>
    </label>
  )
}

export default FundingListPage
