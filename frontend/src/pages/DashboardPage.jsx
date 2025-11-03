import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { applicationsAPI, fundingAPI } from '@/services/api'
import {
  ArrowRight,
  ArrowUpRight,
  Calendar,
  Clock,
  LineChart,
  Sparkles,
  TrendingUp,
} from 'lucide-react'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'

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
        fundingAPI.list({ limit: 8 }),
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

  const statusBreakdown = useMemo(() => {
    return stats.recentApplications.reduce(
      (acc, application) => {
        switch (application.status) {
          case 'in_bearbeitung':
            acc.inProgress += 1
            break
          case 'eingereicht':
            acc.submitted += 1
            break
          case 'genehmigt':
            acc.approved += 1
            break
          default:
            acc.drafts += 1
        }
        return acc
      },
      { inProgress: 0, submitted: 0, approved: 0, drafts: 0 },
    )
  }, [stats.recentApplications])

  const pipelineCompletion = stats.totalApplications
    ? Math.round((statusBreakdown.approved / stats.totalApplications) * 100)
    : 0

  const urgentFundings = stats.recentFundings.filter((funding) => {
    if (!funding.deadline) return false
    const days = Math.ceil((new Date(funding.deadline) - new Date()) / (1000 * 60 * 60 * 24))
    return days > 0 && days <= 30
  })

  const nextDeadline = stats.recentFundings
    .filter((funding) => Boolean(funding.deadline))
    .sort((a, b) => new Date(a.deadline) - new Date(b.deadline))[0]

  if (loading) {
    return <LoadingSpinner text="Dashboard wird geladen..." />
  }

  const ecosystemLevels = [
    {
      id: 'eu',
      title: 'EU-Programme',
      subtitle: 'Mobilität · Innovation · Kooperation',
      points: ['Hohe Budgets ab 500k €', 'Mehrjährige Laufzeit', 'Schulträger zwingend beteiligt'],
    },
    {
      id: 'bund',
      title: 'Bundesebene',
      subtitle: 'Digitalisierung · Startchancen · Ganztag',
      points: ['Cofinanzierung durch Länder', 'Standardisierte Reporting-Struktur', 'Fokus auf Systemtransformation'],
    },
    {
      id: 'laender',
      title: 'Länderprogramme',
      subtitle: 'Regionale Profile & KMK-Schwerpunkte',
      points: ['Schnelle Bewilligung', 'Landesspezifische Kriterien', 'Starke thematische Cluster'],
    },
    {
      id: 'stiftungen',
      title: 'Stiftungen',
      subtitle: 'Pilotprojekte · Beteiligung der Fördervereine',
      points: ['Förderhöhe meist bis 10k €', 'Direkt durch Schule beantragbar', 'Fokus auf Innovation & Teilhabe'],
    },
  ]

  const strategicTracks = [
    {
      title: 'Transformationsprojekte',
      description: 'Für Medienentwicklungspläne, Schulbau und langfristige Programme – ideal, wenn ein erfahrenes Projektteam bereitsteht.',
      highlights: ['EU & Bund', 'Hoher Abstimmungsbedarf', 'Strategische KPIs'],
    },
    {
      title: 'Agile Projektmittel',
      description: 'Für schnelle Pilotierungen, Experimente und Fördervereinsprojekte mit geringer Einstiegshürde und kurzen Formularen.',
      highlights: ['Stiftungen & Länder', 'Genehmigung < 6 Wochen', 'Selbst organisiert'],
    },
    {
      title: 'Kombinationsstrategie',
      description: 'Großprogramme sichern Infrastruktur, agile Projekte testen neue pädagogische Bausteine – parallel geplant für maximale Wirkung.',
      highlights: ['Hybrid-Funding', 'Risikostreuung', 'Schnelle Lerneffekte'],
    },
  ]

  return (
    <div className="space-y-10 animate-fade-in">
      <section className="hero-shell">
        <div className="relative grid gap-10 lg:grid-cols-[1.3fr_1fr]">
          <div className="space-y-6">
            <span className="chip border-transparent bg-brand-navy/10 text-brand-navy">
              <Sparkles className="h-4 w-4" /> KI-orchestriertes Fördermanagement
            </span>
            <div className="space-y-3">
              <h1 className="text-3xl font-semibold text-brand-navy md:text-4xl">
                Ihr personalisiertes Förder-Cockpit
              </h1>
              <p className="max-w-2xl text-base text-slate-600 md:text-lg">
                EduFunds kombiniert semantische Suche, Echtzeit-Status und modulare Insights. Basis für moderne, datengetriebene Entscheidungen im Grundschulbereich.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 text-sm text-slate-600">
              <span className="chip">{stats.activeFundings} aktive Programme</span>
              <span className="chip">{stats.totalApplications} eigene Anträge</span>
              <span className="chip">{statusBreakdown.inProgress} aktuell in Bearbeitung</span>
              <span className="chip">{urgentFundings.length} Fristen &lt; 30 Tage</span>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link to="/funding" className="btn-primary">
                Fördermittel öffnen
                <ArrowUpRight className="h-5 w-5" />
              </Link>
              <Link to="/search" className="btn-secondary">
                KI-Suche starten
              </Link>
            </div>
          </div>

          <div className="rounded-3xl border border-white/70 bg-white/90 p-6 shadow-md">
            <div className="flex items-center justify-between">
              <p className="section-title text-brand-navy/70">Operational Snapshot</p>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
                <TrendingUp className="h-3.5 w-3.5" /> Stabil
              </span>
            </div>
            <div className="mt-5 grid grid-cols-2 gap-3">
              <SnapshotTile
                label="Genehmigungen"
                value={`${statusBreakdown.approved}`}
                caption={`Pipeline-Fortschritt ${pipelineCompletion}%`}
                progress={pipelineCompletion}
              />
              <SnapshotTile
                label="Anträge aktiv"
                value={`${statusBreakdown.inProgress}`}
                caption="Via EduFunds Workflows"
              />
              <SnapshotTile
                label="Neue Programme"
                value={`${stats.recentFundings.length}`}
                caption="Letzte 7 Tage"
              />
              <SnapshotTile
                label="Fristen"
                value={`${urgentFundings.length}`}
                caption="< 30 Tage verbleibend"
              />
            </div>
            <div className="mt-6 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
              {nextDeadline ? (
                <p>
                  Nächste Deadline:{' '}
                  <strong className="text-brand-navy">
                    {new Date(nextDeadline.deadline).toLocaleDateString('de-DE', {
                      day: '2-digit',
                      month: 'long',
                      year: 'numeric',
                    })}
                  </strong>
                  {' · '}
                  {nextDeadline.title}
                </p>
              ) : (
                <p>Keine kritischen Deadlines in den nächsten 30 Tagen.</p>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <KpiCard
          icon={LineChart}
          title="Pipeline"
          value={`${stats.totalApplications}`}
          hint="Verwaltete Anträge"
          meta={`${statusBreakdown.submitted} eingereicht · ${statusBreakdown.approved} genehmigt`}
          progress={pipelineCompletion}
        />
        <KpiCard
          icon={TrendingUp}
          title="Aktive Fördermittel"
          value={`${stats.activeFundings}`}
          hint="Screening in EduFunds"
          meta={`${stats.recentFundings.length} neue Programme`}
        />
        <KpiCard
          icon={Clock}
          title="Fristen Radar"
          value={`${urgentFundings.length}`}
          hint="Akut &lt; 30 Tage"
          meta={nextDeadline ? new Date(nextDeadline.deadline).toLocaleDateString('de-DE') : 'Keine Deadlines'}
        />
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-[2fr_1fr]">
        <div className="space-y-6">
          <div className="card">
            <header className="mb-6 flex flex-wrap items-center gap-4">
              <div>
                <p className="section-title">Meine Anträge</p>
                <h2 className="text-xl font-semibold text-brand-navy">Aktuelle Bearbeitungsschritte</h2>
              </div>
              <Link to="/applications" className="ml-auto inline-flex items-center gap-2 text-sm font-semibold text-brand-navy hover:text-brand-green">
                Alle Anträge
                <ArrowRight className="h-4 w-4" />
              </Link>
            </header>

            {stats.recentApplications.length === 0 ? (
              <EmptyState
                title="Noch keine Anträge"
                description="Legen Sie Ihren ersten KI-gestützten Förderantrag an."
                action={
                  <Link to="/funding" className="btn-primary text-sm">
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

          <div className="card">
            <header className="mb-6 flex flex-wrap items-center gap-4">
              <div>
                <p className="section-title">Neue Fördermittel</p>
                <h2 className="text-xl font-semibold text-brand-navy">Kuratiert für Grundschulen</h2>
              </div>
              <Link to="/funding" className="ml-auto inline-flex items-center gap-2 text-sm font-semibold text-brand-navy hover:text-brand-green">
                Alle Programme
                <ArrowRight className="h-4 w-4" />
              </Link>
            </header>

            {stats.recentFundings.length === 0 ? (
              <div className="py-10 text-center text-slate-500">
                <p>Keine neuen Programme verfügbar.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {stats.recentFundings.map((funding, index) => {
                  const key =
                    funding.funding_id ||
                    funding.id ||
                    funding.uuid ||
                    funding.slug ||
                    `recent-funding-${index}`
                  return <FundingCard key={key} funding={funding} />
                })}
              </div>
            )}
          </div>
        </div>

        <aside className="space-y-4">
          <div className="card">
            <p className="section-title">Förder-Landschaft</p>
            <h3 className="mt-2 text-lg font-semibold text-brand-navy">Vier Ebenen · Ein Blick</h3>
            <p className="mt-3 text-sm text-slate-600">
              EduFunds verknüpft komplexe Förderlandschaften zu einem stringenten Entscheidungs-Framework – inklusive KI-Empfehlungen pro Ebene.
            </p>
          </div>

          {ecosystemLevels.map((level) => (
            <article key={level.id} className="card">
              <h4 className="text-base font-semibold text-brand-navy">{level.title}</h4>
              <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">{level.subtitle}</p>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                {level.points.map((point) => (
                  <li key={point} className="flex items-start gap-2">
                    <span className="mt-1 h-1.5 w-1.5 rounded-full bg-brand-green"></span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </aside>
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {strategicTracks.map((track) => (
          <InsightCard key={track.title} track={track} />
        ))}
      </section>

      <section className="card bg-gradient-to-r from-brand-navy to-primary-700 text-white">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-3xl space-y-3">
            <p className="section-title text-white/70">Next Step</p>
            <h3 className="text-2xl font-semibold">Institutionelle Roadmap + agile Experimente kombinieren</h3>
            <p className="text-sm text-white/80">
              Planen Sie Großvorhaben mit Schulträgern und testen Sie parallel agile Initiativen mit Fördervereinen. EduFunds liefert Templates, KI-Drafts und Monitoring in einem Workflow.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link to="/applications" className="btn-secondary bg-white text-brand-navy">
              Workspace öffnen
            </Link>
            <Link to="/search" className="btn-ghost text-white">
              Semantische Suche
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

function KpiCard({ icon: Icon, title, value, hint, meta, progress }) {
  return (
    <div className="kpi-card">
      <div className="flex items-start justify-between">
        <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-navy/10 text-brand-navy">
          <Icon className="h-6 w-6" />
        </span>
        {meta && <span className="kpi-trend bg-brand-navy/10 text-brand-navy">{meta}</span>}
      </div>
      <div className="mt-6 space-y-2">
        <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">{title}</p>
        <p className="text-3xl font-semibold text-brand-navy">{value}</p>
        <p className="text-sm text-slate-500">{hint}</p>
      </div>
      {typeof progress === 'number' && !Number.isNaN(progress) && (
        <div className="mt-5 h-2 w-full overflow-hidden rounded-full bg-slate-200">
          <span
            className="block h-full rounded-full bg-gradient-to-r from-primary-600 to-brand-green"
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      )}
    </div>
  )
}

function SnapshotTile({ label, value, caption, progress }) {
  return (
    <div className="rounded-2xl border border-slate-200/70 bg-white/90 p-4 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-brand-navy">{value}</p>
      <p className="mt-1 text-xs text-slate-500">{caption}</p>
      {typeof progress === 'number' && !Number.isNaN(progress) && (
        <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
          <span
            className="block h-full rounded-full bg-gradient-to-r from-primary-600 to-brand-green"
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      )}
    </div>
  )
}

function ApplicationCard({ app }) {
  return (
    <Link
      to={`/applications/${app.application_id}`}
      className="group rounded-3xl border border-slate-200/70 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-2">
          <h3 className="text-base font-semibold text-brand-navy group-hover:text-primary-600">{app.title}</h3>
          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="inline-flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" />
              {new Date(app.created_at).toLocaleDateString('de-DE')}
            </span>
          </div>
        </div>
        <StatusBadge status={app.status} />
      </div>
    </Link>
  )
}

function FundingCard({ funding }) {
  const fundingId = funding.funding_id ?? funding.id ?? funding.uuid ?? funding.slug
  const deadline = funding.deadline ? new Date(funding.deadline).toLocaleDateString('de-DE') : null
  return (
    <Link
      to={fundingId ? `/funding/${fundingId}` : '#'}
      className="group rounded-3xl border border-slate-200/70 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
    >
      <div className="space-y-3">
        <div>
          <h3 className="text-base font-semibold text-brand-navy group-hover:text-primary-600 line-clamp-2">{funding.title}</h3>
          <p className="mt-1 text-xs text-slate-500">{funding.provider || 'Unbekannter Fördergeber'}</p>
        </div>
        {funding.cleaned_text && (
          <p className="text-sm text-slate-600 line-clamp-3">{funding.cleaned_text}</p>
        )}
        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
          {deadline && (
            <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-slate-600">
              <Clock className="h-3.5 w-3.5" />
              {deadline}
            </span>
          )}
          {funding.funding_area && <span className="badge-soft">{funding.funding_area}</span>}
        </div>
      </div>
    </Link>
  )
}

function StatusBadge({ status }) {
  const variants = {
    entwurf: 'bg-slate-100 text-slate-700 border-slate-200',
    in_bearbeitung: 'bg-sky-100 text-sky-700 border-sky-200',
    eingereicht: 'bg-amber-100 text-amber-700 border-amber-200',
    genehmigt: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    abgelehnt: 'bg-rose-100 text-rose-700 border-rose-200',
  }

  const labels = {
    entwurf: 'Entwurf',
    in_bearbeitung: 'In Bearbeitung',
    eingereicht: 'Eingereicht',
    genehmigt: 'Genehmigt',
    abgelehnt: 'Abgelehnt',
  }

  return <span className={`badge border ${variants[status]}`}>{labels[status]}</span>
}

function InsightCard({ track }) {
  return (
    <div className="card">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Strategische Route</p>
      <h3 className="mt-2 text-lg font-semibold text-brand-navy">{track.title}</h3>
      <p className="mt-3 text-sm text-slate-600">{track.description}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {track.highlights.map((highlight) => (
          <span key={highlight} className="badge-soft text-xs">
            {highlight}
          </span>
        ))}
      </div>
    </div>
  )
}

export default DashboardPage
