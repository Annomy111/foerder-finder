import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { searchAPI, fundingAPI } from '@/services/api'
import {
  Search,
  Sparkles,
  Zap,
  MapPin,
  TrendingUp,
  Clock,
  Info,
  X,
  Loader2,
  Building2,
  FileText,
  ArrowRight,
} from 'lucide-react'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'
import InfoBox from '@/components/ui/InfoBox'

/**
 * Alle 16 Bundesländer für Filter
 */
const BUNDESLAENDER = [
  { value: '', label: 'Alle Bundesländer' },
  { value: 'Bundesweit', label: 'Bundesweit' },
  { value: 'Baden-Württemberg', label: 'Baden-Württemberg' },
  { value: 'Bayern', label: 'Bayern' },
  { value: 'Berlin', label: 'Berlin' },
  { value: 'Brandenburg', label: 'Brandenburg' },
  { value: 'Bremen', label: 'Bremen' },
  { value: 'Hamburg', label: 'Hamburg' },
  { value: 'Hessen', label: 'Hessen' },
  { value: 'Mecklenburg-Vorpommern', label: 'Mecklenburg-Vorpommern' },
  { value: 'Niedersachsen', label: 'Niedersachsen' },
  { value: 'Nordrhein-Westfalen', label: 'Nordrhein-Westfalen' },
  { value: 'Rheinland-Pfalz', label: 'Rheinland-Pfalz' },
  { value: 'Saarland', label: 'Saarland' },
  { value: 'Sachsen', label: 'Sachsen' },
  { value: 'Sachsen-Anhalt', label: 'Sachsen-Anhalt' },
  { value: 'Schleswig-Holstein', label: 'Schleswig-Holstein' },
  { value: 'Thüringen', label: 'Thüringen' },
]

/**
 * Smart Search Page - RAG-powered semantic search
 */
function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchMode, setSearchMode] = useState('advanced') // 'advanced' or 'quick'
  const [region, setRegion] = useState('')
  const [topK, setTopK] = useState(10)
  const [expandQueries, setExpandQueries] = useState(true)
  const [rerankResults, setRerankResults] = useState(true)
  const [searchMetadata, setSearchMetadata] = useState(null)
  const [fundingDetails, setFundingDetails] = useState({})

  const handleSearch = useCallback(async () => {
    if (query.trim().length < 3) {
      return
    }

    setLoading(true)
    try {
      let payload
      if (searchMode === 'quick') {
        const data = await searchAPI.quickSearch(query, topK)
        payload = data
      } else {
        const data = await searchAPI.search({
          query: query.trim(),
          top_k: topK,
          region: region || undefined,
          expand_queries: expandQueries,
          rerank_results: rerankResults,
        })
        payload = data
      }

      const fetchedResults = payload?.results || []
      setResults(fetchedResults)
      setSearchMetadata(payload)

      const uniqueFundingIds = [...new Set(fetchedResults.map((r) => r.funding_id).filter(Boolean))]
      const details = {}
      await Promise.all(
        uniqueFundingIds.map(async (id) => {
          try {
            const funding = await fundingAPI.getById(id)
            details[id] = funding
          } catch (error) {
            console.error(`Failed to fetch funding ${id}:`, error)
          }
        })
      )
      setFundingDetails(details)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }, [query, searchMode, topK, region, expandQueries, rerankResults])

  useEffect(() => {
    if (query.length < 3) {
      return
    }

    const debounceTimer = setTimeout(() => {
      handleSearch()
    }, 500)

    return () => clearTimeout(debounceTimer)
  }, [query, handleSearch])

  const clearSearch = () => {
    setQuery('')
    setResults([])
    setSearchMetadata(null)
    setFundingDetails({})
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-3">
        <span className="chip border-transparent bg-brand-navy/10 text-brand-navy">
          <Sparkles size={14} /> KI-gestützte Suche
        </span>
        <div>
          <h1 className="text-4xl font-semibold text-brand-navy">
            Intelligente Fördermittel-Suche
          </h1>
          <p className="max-w-2xl text-base text-slate-500">
            Nutzen Sie KI-basierte semantische Suche, um die perfekten Förderprogramme für Ihre Grundschule zu finden.
            Durchsuchen Sie 1,730+ Dokumente aus allen 16 Bundesländern.
          </p>
        </div>
      </div>

      {/* Info Banner */}
      <InfoBox variant="info" className="border-dashed">
        <div className="flex items-start gap-3">
          <Info size={20} className="mt-0.5" />
          <div>
            <h3 className="font-semibold text-brand-navy">Wie funktioniert die semantische Suche?</h3>
            <p className="text-sm text-slate-600">
              Unsere KI versteht die <strong>Bedeutung</strong> Ihrer Anfrage, nicht nur Schlüsselwörter.
              Suchen Sie nach „Tablets für Mathe-Unterricht“ und finden Sie auch „DigitalPakt MINT-Bildung“.
              Powered by BGE-M3 Embeddings + BM25 Hybrid Search + Cross-Encoder Reranking.
            </p>
          </div>
        </div>
      </InfoBox>

      {/* Search Box */}
      <div className="card">
        <div className="space-y-4">
          {/* Main Search Input */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-brand-navy/40" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="z.B. 'Tablets für Grundschule in Berlin', 'MINT-Förderung NRW', 'Leseförderung Startchancen'..."
              className="w-full rounded-2xl border border-brand-navy/10 bg-white/80 py-4 pl-12 pr-12 text-base font-medium text-brand-navy placeholder-slate-400 shadow-inner focus:border-brand-green focus:outline-none focus:ring-2 focus:ring-brand-green/20"
            />
            {query && (
              <button
                onClick={clearSearch}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-brand-navy"
              >
                <X size={20} />
              </button>
            )}
          </div>

          {/* Search Options */}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            {/* Search Mode */}
            <div className="space-y-2">
              <label className="label">Suchmodus</label>
              <div className="flex gap-2">
                <button
                  onClick={() => setSearchMode('advanced')}
                  className={`flex-1 rounded-xl border px-3 py-2 text-sm font-semibold transition-all ${
                    searchMode === 'advanced'
                      ? 'border-brand-green bg-brand-green text-white'
                      : 'border-brand-navy/20 bg-white text-brand-navy hover:border-brand-green'
                  }`}
                >
                  <Sparkles size={14} className="inline mr-1" />
                  Advanced
                </button>
                <button
                  onClick={() => setSearchMode('quick')}
                  className={`flex-1 rounded-xl border px-3 py-2 text-sm font-semibold transition-all ${
                    searchMode === 'quick'
                      ? 'border-brand-green bg-brand-green text-white'
                      : 'border-brand-navy/20 bg-white text-brand-navy hover:border-brand-green'
                  }`}
                >
                  <Zap size={14} className="inline mr-1" />
                  Quick
                </button>
              </div>
            </div>

            {/* Region Filter */}
            <div className="space-y-2">
              <label className="label">Bundesland</label>
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full rounded-xl border border-brand-navy/10 bg-white/80 px-4 py-2 text-sm font-medium text-brand-navy focus:border-brand-green focus:outline-none focus:ring-2 focus:ring-brand-green/20"
              >
                {BUNDESLAENDER.map((land) => (
                  <option key={land.value} value={land.value}>
                    {land.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Results Count */}
            <div className="space-y-2">
              <label className="label">Ergebnisse</label>
              <select
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full rounded-xl border border-brand-navy/10 bg-white/80 px-4 py-2 text-sm font-medium text-brand-navy focus:border-brand-green focus:outline-none focus:ring-2 focus:ring-brand-green/20"
              >
                <option value={5}>Top 5</option>
                <option value={10}>Top 10</option>
                <option value={20}>Top 20</option>
                <option value={50}>Top 50</option>
              </select>
            </div>

            {/* Search Button */}
            <div className="space-y-2">
              <label className="label">&nbsp;</label>
              <button
                onClick={handleSearch}
                disabled={loading || query.trim().length < 3}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    Suche läuft...
                  </>
                ) : (
                  <>
                    <Search size={18} />
                    Suchen
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Advanced Options (only in advanced mode) */}
          {searchMode === 'advanced' && (
            <div className="flex flex-wrap gap-4 border-t border-brand-navy/10 pt-4">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={expandQueries}
                  onChange={(e) => setExpandQueries(e.target.checked)}
                  className="h-4 w-4 rounded border-brand-navy/20 text-brand-green focus:ring-brand-green"
                />
                <span className="font-medium text-brand-navy">Query Expansion (RAG Fusion)</span>
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={rerankResults}
                  onChange={(e) => setRerankResults(e.target.checked)}
                  className="h-4 w-4 rounded border-brand-navy/20 text-brand-green focus:ring-brand-green"
                />
                <span className="font-medium text-brand-navy">Cross-Encoder Reranking</span>
              </label>
            </div>
          )}
        </div>
      </div>

      {/* Search Metadata */}
      {searchMetadata && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <MetricCard
            icon={FileText}
            label="Ergebnisse"
            value={searchMetadata.total_results || 0}
            color="text-brand-navy"
          />
          <MetricCard
            icon={Clock}
            label="Antwortzeit"
            value={`${(searchMetadata.retrieval_time_ms || 0).toFixed(0)}ms`}
            color="text-emerald-600"
          />
          <MetricCard
            icon={Sparkles}
            label="Pipeline"
            value={searchMode === 'advanced' ? 'Advanced RAG' : 'Quick'}
            color="text-purple-600"
          />
          <MetricCard
            icon={TrendingUp}
            label="RAG Features"
            value={`${Object.values(searchMetadata.pipeline_config || {}).filter(Boolean).length}/4`}
            color="text-amber-600"
          />
        </div>
      )}

      {/* Results */}
      {loading ? (
        <LoadingSpinner text="KI durchsucht 1,730+ Dokumente..." />
      ) : results.length > 0 ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-brand-navy">
              {results.length} Relevante Ergebnisse für „{query}“
            </h2>
            {region && (
              <span className="badge-soft">
                <MapPin size={14} className="inline mr-1" />
                {region}
              </span>
            )}
          </div>

          {results.map((result, index) => (
            <SearchResultCard
              key={result.chunk_id}
              result={result}
              index={index}
              fundingDetails={fundingDetails[result.funding_id]}
            />
          ))}
        </div>
      ) : query.trim().length >= 3 && !loading ? (
        <EmptyState
          title="Keine Ergebnisse gefunden"
          description="Versuchen Sie andere Suchbegriffe oder passen Sie die Filter an."
          action={
            <button onClick={clearSearch} className="btn-primary">
              Suche zurücksetzen
            </button>
          }
        />
      ) : (
        <div className="card text-center">
          <Search size={48} className="mx-auto mb-4 text-brand-navy/20" />
          <h3 className="mb-2 text-lg font-semibold text-brand-navy">
            Starten Sie Ihre Suche
          </h3>
          <p className="text-sm text-slate-500">
            Geben Sie mindestens 3 Zeichen ein, um die semantische Suche zu starten.
          </p>
        </div>
      )}
    </div>
  )
}

/**
 * Search Result Card Component
 */
function SearchResultCard({ result, index, fundingDetails }) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="card group hover:shadow-lg transition-all">
      {/* Rank Badge */}
      <div className="mb-3 flex items-center justify-between">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-brand-navy/10 text-sm font-bold text-brand-navy">
          #{index + 1}
        </span>
        <div className="flex items-center gap-2">
          {/* Relevance Score */}
          <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
            Score: {result.score.toFixed(4)}
          </span>
          {/* Region */}
          {result.metadata.region && (
            <span className="badge-soft">
              <MapPin size={12} className="inline mr-1" />
              {result.metadata.region}
            </span>
          )}
        </div>
      </div>

      {/* Title (from funding details if available) */}
      {fundingDetails && (
        <div className="mb-3">
          <Link
            to={`/funding/${result.funding_id}`}
            className="text-xl font-semibold text-brand-navy hover:text-brand-green transition-colors"
          >
            {fundingDetails.title}
          </Link>
          <div className="mt-1 flex items-center gap-2 text-sm text-slate-600">
            <Building2 size={14} />
            <span>{result.metadata.provider || 'Keine Angabe'}</span>
          </div>
        </div>
      )}

      {/* Matched Text Snippet */}
      <div className="mb-4">
        <p className={`text-sm leading-relaxed text-slate-700 ${isExpanded ? '' : 'line-clamp-3'}`}>
          {result.text}
        </p>
        {result.text.length > 200 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-2 text-xs font-semibold text-brand-green hover:text-brand-navy"
          >
            {isExpanded ? 'Weniger anzeigen' : 'Mehr anzeigen'}
          </button>
        )}
      </div>

      {/* Metadata Tags */}
      <div className="flex flex-wrap gap-2 border-t border-brand-navy/10 pt-3">
        {result.metadata.funding_area && (
          <span className="badge bg-purple-100 text-purple-700">
            {result.metadata.funding_area}
          </span>
        )}
        <span className="badge bg-slate-100 text-slate-600">
          Chunk ID: {result.chunk_id.slice(0, 8)}...
        </span>
      </div>

      {/* Action Button */}
      <Link
        to={`/funding/${result.funding_id}`}
        className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-brand-green hover:text-brand-navy transition-colors"
      >
        Details ansehen
        <ArrowRight size={16} />
      </Link>
    </div>
  )
}

/**
 * Metric Card Component
 */
function MetricCard({ icon: IconComponent, label, value, color }) {
  return (
    <div className="rounded-3xl border border-slate-200/80 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-navy/10 text-brand-navy">
          <IconComponent size={20} className={color} />
        </span>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
          <p className="text-lg font-semibold text-brand-navy">{value}</p>
        </div>
      </div>
    </div>
  )
}

export default SearchPage
