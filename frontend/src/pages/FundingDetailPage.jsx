import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { fundingAPI, applicationsAPI } from '@/services/api'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Calendar,
  Building2,
  Euro,
  ExternalLink,
  Sparkles,
  CheckCircle,
  AlertCircle,
  FileText,
  Target,
  Lightbulb,
  Info,
  ArrowRight,
  Check,
  HelpCircle,
  BookmarkCheck,
  Users,
  Download,
} from 'lucide-react'
import LoadingSpinner from '@/components/LoadingSpinner'
import InfoBox from '@/components/ui/InfoBox'

// Helper function to clean and format description
function cleanDescription(text) {
  if (!text) return ''

  // Remove image markdown/HTML
  let cleaned = text
    .replace(/!\[.*?\]\(.*?\)/g, '') // Remove markdown images
    .replace(/<img[^>]*>/g, '') // Remove HTML images
    .replace(/\[!\[.*?\]\(.*?\)\]\(.*?\)/g, '') // Remove linked images

  // Limit length
  if (cleaned.length > 3000) {
    cleaned = cleaned.substring(0, 3000) + '...'
  }

  return cleaned.trim()
}

// Helper function to get display title
function getDisplayTitle(funding) {
  if (!funding) return ''
  if (funding.title && funding.title !== 'Unbekannt') return funding.title
  if (funding.provider) return funding.provider
  return 'Förderprogramm'
}

function FundingDetailPage() {
  const { fundingId } = useParams()
  const navigate = useNavigate()
  const [funding, setFunding] = useState(null)
  const [loading, setLoading] = useState(true)
  const [applying, setApplying] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')
  const [exporting, setExporting] = useState(false)

  const deriveNumericAmount = (value) => {
    if (value === null || value === undefined) return null
    const numeric = Number(value)
    return Number.isFinite(numeric) ? numeric : null
  }

  // Lazy load DOCX export (only when user clicks export button)
  const handleExportDocx = async () => {
    setExporting(true)
    try {
      const { exportFundingToDocx } = await import('@/utils/exportDocx')
      await exportFundingToDocx(funding)
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setExporting(false)
    }
  }

  useEffect(() => {
    let isMounted = true

    const fetchFunding = async () => {
      try {
        setLoading(true)
        const data = await fundingAPI.getById(fundingId)
        if (isMounted) {
          setFunding(data)
        }
      } catch (error) {
        if (isMounted) {
          console.error('Fehler:', error)
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchFunding()

    return () => {
      isMounted = false
    }
  }, [fundingId])

  const handleApplyWithAI = async () => {
    if (!funding) return

    const fundingIdentifier =
      funding.funding_id ??
      funding.id ??
      funding.uuid ??
      funding.slug ??
      fundingId

    if (!fundingIdentifier) {
      alert('Für dieses Förderprogramm konnte keine eindeutige ID ermittelt werden.')
      return
    }

    setApplying(true)
    try {
      const newApp = await applicationsAPI.create({
        funding_id: fundingIdentifier,
        title: `Antrag: ${getDisplayTitle(funding)}`,
        projektbeschreibung: '',
      })
      const applicationId = newApp?.application_id ?? newApp?.id
      navigate(applicationId ? `/applications/${applicationId}` : '/applications')
    } catch (error) {
      console.error('Fehler beim Erstellen des Antrags:', error)
      alert('Fehler beim Erstellen des Antrags. Bitte versuchen Sie es erneut.')
    } finally {
      setApplying(false)
    }
  }

  if (loading) {
    return <LoadingSpinner text="Fördermittel werden geladen..." />
  }

  if (!funding) {
    return (
      <div className="text-center py-12">
        <AlertCircle size={64} className="mx-auto text-red-500 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Nicht gefunden</h2>
        <p className="text-gray-600 mb-6">Diese Förderung existiert nicht oder wurde gelöscht.</p>
        <button onClick={() => navigate('/funding')} className="btn-primary">
          Zurück zur Übersicht
        </button>
      </div>
    )
  }

  const daysUntilDeadline = funding.deadline
    ? Math.ceil((new Date(funding.deadline) - new Date()) / (1000 * 60 * 60 * 24))
    : null

  const isUrgent = daysUntilDeadline !== null && daysUntilDeadline < 7

  const minFundingAmount = deriveNumericAmount(
    funding.min_funding_amount ??
      funding.amount_min ??
      funding.minimum_amount ??
      funding.min_amount ??
      (typeof funding.amount === 'object' ? funding.amount?.min : null)
  )

  const maxFundingAmount = deriveNumericAmount(
    funding.max_funding_amount ??
      funding.amount_max ??
      funding.maximum_amount ??
      funding.max_amount ??
      (typeof funding.amount === 'object' ? funding.amount?.max : null)
  )

  const tabs = [
    { id: 'overview', label: 'Übersicht', icon: Info },
    { id: 'requirements', label: 'Voraussetzungen', icon: CheckCircle },
    { id: 'application', label: 'Antragstellung', icon: FileText },
    { id: 'faq', label: 'FAQ', icon: HelpCircle },
  ]

  return (
    <div className="space-y-6">
      <nav className="flex items-center gap-2 text-sm text-slate-500">
        <button onClick={() => navigate('/funding')} className="btn-ghost px-0 text-slate-500 hover:text-brand-navy">
          Fördermittel
        </button>
        <ArrowRight size={16} />
        <span className="truncate font-medium text-brand-navy">{funding.title}</span>
      </nav>

      <section className="relative overflow-hidden rounded-3xl border border-brand-navy/10 bg-gradient-to-br from-white via-brand-navy/5 to-white p-6 shadow-soft">
        <div className="absolute -right-10 top-6 h-28 w-28 rounded-full bg-brand-green/20 blur-3xl" />
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              {isUrgent && <span className="badge-danger">Dringend</span>}
              <span className="badge-soft">Aktive Förderung</span>
            </div>
            <h1 className="text-4xl font-semibold text-brand-navy">{getDisplayTitle(funding)}</h1>
            <div className="flex items-center gap-2 text-lg text-slate-500">
              <Building2 size={20} />
              <span className="font-semibold text-brand-navy">{funding.provider || 'Nicht verfügbar'}</span>
            </div>
          </div>

          <div className="flex flex-col gap-3 lg:min-w-[260px]">
            <button onClick={handleApplyWithAI} disabled={applying} className="btn-primary w-full text-base">
              <Sparkles size={20} />
              <span>{applying ? 'Wird erstellt…' : 'Mit KI beantragen'}</span>
            </button>
            <InfoBox variant="success" title="KI-Vorteil" icon={BookmarkCheck}>
              Ihre Projektdaten werden automatisch übernommen. Der Entwurf lässt sich jederzeit anpassen.
            </InfoBox>
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">
          {funding.deadline && (
            <article className={`rounded-3xl border px-5 py-4 ${
              isUrgent ? 'border-red-300 bg-red-100' : 'border-brand-navy/10 bg-white/80'
            }`}>
              <div className="flex items-center gap-3">
                <Calendar size={28} className={isUrgent ? 'text-red-600' : 'text-brand-navy'} />
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Antragsfrist</p>
                  <p className="text-lg font-semibold text-brand-navy">
                    {new Date(funding.deadline).toLocaleDateString('de-DE', {
                      day: '2-digit',
                      month: 'long',
                      year: 'numeric',
                    })}
                  </p>
                  {daysUntilDeadline !== null && daysUntilDeadline > 0 && (
                    <p className={`text-sm font-medium ${isUrgent ? 'text-red-700' : 'text-brand-green'}`}>
                      Noch {daysUntilDeadline} Tage
                    </p>
                  )}
                </div>
              </div>
            </article>
          )}

          {(minFundingAmount !== null || maxFundingAmount !== null) && (
            <article className="rounded-3xl border border-emerald-500/20 bg-emerald-500/10 px-5 py-4">
              <div className="flex items-center gap-3">
                <Euro size={28} className="text-emerald-600" />
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Fördersumme</p>
                  <p className="text-lg font-semibold text-brand-navy">
                    {minFundingAmount !== null ? `${minFundingAmount.toLocaleString('de-DE')}€` : '—'}
                    {minFundingAmount !== null && maxFundingAmount !== null && ' – '}
                    {maxFundingAmount !== null ? `${maxFundingAmount.toLocaleString('de-DE')}€` : minFundingAmount !== null ? 'bis offen' : '—'}
                  </p>
                </div>
              </div>
            </article>
          )}

          {funding.target_groups && funding.target_groups.length > 0 && (
            <article className="rounded-3xl border border-brand-navy/10 bg-white/80 px-5 py-4">
              <div className="flex items-center gap-3">
                <Users size={28} className="text-brand-navy" />
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Zielgruppe</p>
                  <p className="text-lg font-semibold text-brand-navy line-clamp-2">
                    {funding.target_groups.slice(0, 2).join(', ')}
                  </p>
                </div>
              </div>
            </article>
          )}
        </div>
      </section>

      {/* Tabs */}
      <div className="border-b-2 border-gray-200 bg-gradient-to-r from-white to-slate-50">
        <nav className="flex gap-2 px-2">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-4 font-semibold transition-all rounded-t-xl ${
                  activeTab === tab.id
                    ? 'bg-white text-primary-600 border-t-4 border-primary-600 shadow-md -mb-0.5'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <Icon size={20} />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-5 lg:col-span-2">
          {activeTab === 'overview' && (
            <>
              <div className="card">
                <h2 className="mb-3 flex items-center gap-2 text-xl font-semibold text-brand-navy">
                  <Info size={22} className="text-brand-green" /> Programmbeschreibung
                </h2>
                <div className="prose prose-slate max-w-none text-slate-700">
                  {funding.cleaned_text || funding.description ? (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        // Remove images from rendering
                        img: () => null,
                        // Style headings
                        h1: (props) => <h2 className="text-2xl font-bold text-brand-navy mt-6 mb-3" {...props} />,
                        h2: (props) => <h3 className="text-xl font-semibold text-brand-navy mt-5 mb-2" {...props} />,
                        h3: (props) => <h4 className="text-lg font-medium text-brand-navy mt-4 mb-2" {...props} />,
                        // Style lists
                        ul: (props) => <ul className="list-disc pl-6 space-y-2 my-4" {...props} />,
                        ol: (props) => <ol className="list-decimal pl-6 space-y-2 my-4" {...props} />,
                        li: (props) => <li className="leading-7" {...props} />,
                        // Style paragraphs
                        p: (props) => <p className="leading-7 text-base mb-4" {...props} />,
                        // Style links
                        a: (props) => (
                          <a className="text-brand-teal hover:underline font-medium" target="_blank" rel="noopener noreferrer" {...props} />
                        ),
                      }}
                    >
                      {cleanDescription(funding.cleaned_text || funding.description)}
                    </ReactMarkdown>
                  ) : (
                    <p className="leading-7 text-base text-slate-500 italic">
                      Keine Beschreibung verfügbar.
                    </p>
                  )}
                </div>
              </div>

              {funding.eligible_costs && funding.eligible_costs.length > 0 && (
                <div className="card border-emerald-500/20 bg-emerald-500/10">
                  <h2 className="mb-3 flex items-center gap-2 text-xl font-semibold text-brand-navy">
                    <Check size={22} className="text-emerald-600" /> Was wird gefördert?
                  </h2>
                  <ul className="space-y-3">
                    {funding.eligible_costs.map((cost, index) => (
                      <li key={index} className="flex items-start space-x-3">
                        <Check className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
                        <span className="text-gray-700">{cost}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Display eligibility criteria if available */}
              {funding.eligibility && funding.eligibility.length > 0 && (
                <div className="card border-blue-200 bg-blue-50">
                  <h2 className="mb-3 flex items-center gap-2 text-xl font-semibold text-blue-900">
                    <CheckCircle size={22} className="text-blue-600" /> Fördervoraussetzungen
                  </h2>
                  <ul className="space-y-3">
                    {funding.eligibility.map((criterion, index) => (
                      <li key={index} className="flex items-start space-x-3">
                        <CheckCircle className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
                        <span className="text-gray-700">{criterion}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Display target groups if available */}
              {funding.target_groups && funding.target_groups.length > 0 && (
                <div className="card border-purple-200 bg-purple-50">
                  <h2 className="mb-3 flex items-center gap-2 text-xl font-semibold text-purple-900">
                    <Users size={22} className="text-purple-600" /> Zielgruppen
                  </h2>
                  <ul className="space-y-3">
                    {funding.target_groups.map((group, index) => (
                      <li key={index} className="flex items-start space-x-3">
                        <Users className="text-purple-600 flex-shrink-0 mt-0.5" size={20} />
                        <span className="text-gray-700">{group}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}

          {activeTab === 'requirements' && (
            <>
              {funding.requirements && funding.requirements.length > 0 && (
                <div className="card border-orange-200 bg-orange-50">
                  <h2 className="mb-3 flex items-center gap-2 text-xl font-semibold text-orange-900">
                    <FileText size={22} className="text-orange-600" /> Erforderliche Nachweise
                  </h2>
                  <ul className="space-y-3">
                    {funding.requirements.map((req, index) => (
                      <li key={index} className="flex items-start space-x-3">
                        <FileText className="text-orange-600 flex-shrink-0 mt-0.5" size={20} />
                        <span className="text-gray-700">{req}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {funding.evaluation_criteria && funding.evaluation_criteria.length > 0 && (
                <div className="card border-emerald-500/20 bg-emerald-500/10">
                  <h2 className="mb-3 flex items-center gap-2 text-xl font-semibold text-brand-navy">
                    <Target className="text-emerald-600" size={22} /> Bewertungskriterien
                  </h2>
                  <p className="text-gray-700 mb-3">Ihr Antrag wird nach folgenden Kriterien bewertet:</p>
                  <ul className="space-y-3">
                    {funding.evaluation_criteria.map((criterion, index) => (
                      <li key={index} className="flex items-start space-x-3 p-3 bg-white rounded-lg border border-green-200">
                        <Target className="text-emerald-600 flex-shrink-0 mt-0.5" size={20} />
                        <span className="text-gray-700">{criterion}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}

          {activeTab === 'application' && (
            <>
              <div className="card border-brand-navy/15 bg-brand-navy/5">
                <div className="flex items-start gap-4">
                  <Sparkles className="mt-1 flex-shrink-0 text-brand-green" size={32} />
                  <div>
                    <h2 className="text-2xl font-semibold text-brand-navy">KI-gestützte Antragstellung in 5 Schritten</h2>
                    <p className="mt-3 text-slate-600">
                      Nutzen Sie unsere KI, um alle formalen Anforderungen sicher zu erfüllen und in Minuten einen strukturierten Antrag zu erhalten.
                    </p>
                    <ol className="mt-6 space-y-4">
                      {[
                        {
                          step: 1,
                          title: 'Antrag erstellen',
                          desc: 'Klicken Sie auf "Mit KI beantragen" - ein neuer Antragsentwurf wird angelegt'
                        },
                        {
                          step: 2,
                          title: 'Projektidee beschreiben',
                          desc: 'Beschreiben Sie Ihre Projektidee in 2-3 Sätzen (z.B. "Wir möchten einen Schulgarten anlegen...")'
                        },
                        {
                          step: 3,
                          title: 'KI-Entwurf generieren',
                          desc: 'Die KI erstellt einen vollständigen Antragsentwurf basierend auf den Förderrichtlinien'
                        },
                        {
                          step: 4,
                          title: 'Entwurf anpassen',
                          desc: 'Prüfen und bearbeiten Sie den Entwurf nach Ihren Wünschen'
                        },
                        {
                          step: 5,
                          title: 'Antrag einreichen',
                          desc: 'Exportieren Sie den Antrag und reichen Sie ihn beim Fördergeber ein'
                        }
                      ].map((item) => (
                        <li key={item.step} className="flex items-start space-x-4">
                          <div className="flex-shrink-0 w-10 h-10 bg-primary-500 text-white rounded-full flex items-center justify-center font-bold">
                            {item.step}
                          </div>
                          <div>
                            <h3 className="font-bold text-gray-900 mb-1">{item.title}</h3>
                            <p className="text-gray-600">{item.desc}</p>
                          </div>
                        </li>
                      ))}
                    </ol>
                    <button onClick={handleApplyWithAI} disabled={applying} className="btn-primary mt-6 w-full">
                      <Sparkles size={20} />
                      <span>{applying ? 'Wird erstellt…' : 'Jetzt KI-Antrag starten'}</span>
                    </button>
                  </div>
                </div>
              </div>

              <div className="card">
                <h2 className="mb-4 flex items-center gap-3 text-xl font-semibold text-brand-navy">
                  <Lightbulb className="text-amber-500" size={24} /> Tipps für einen erfolgreichen Antrag
                </h2>
                <ul className="space-y-3 text-gray-700">
                  <li className="flex items-start space-x-3">
                    <span className="text-primary-600 font-bold">→</span>
                    <span><strong>Konkret bleiben:</strong> Beschreiben Sie Ihr Projekt spezifisch mit klaren Zielen und Maßnahmen</span>
                  </li>
                  <li className="flex items-start space-x-3">
                    <span className="text-primary-600 font-bold">→</span>
                    <span><strong>Budget realistisch kalkulieren:</strong> Alle Kosten müssen nachvollziehbar und marktüblich sein</span>
                  </li>
                  <li className="flex items-start space-x-3">
                    <span className="text-primary-600 font-bold">→</span>
                    <span><strong>Nachhaltigkeit betonen:</strong> Zeigen Sie, wie das Projekt langfristig wirkt</span>
                  </li>
                  <li className="flex items-start space-x-3">
                    <span className="text-primary-600 font-bold">→</span>
                    <span><strong>Fristen beachten:</strong> Reichen Sie den Antrag rechtzeitig ein (min. 1 Woche vor Deadline)</span>
                  </li>
                </ul>
              </div>
            </>
          )}

          {activeTab === 'faq' && (
            <div className="card">
              <h2 className="mb-6 flex items-center gap-3 text-2xl font-semibold text-brand-navy">
                <HelpCircle className="text-brand-green" size={24} /> Häufig gestellte Fragen
              </h2>
              <div className="space-y-4">
                {[
                  {
                    q: 'Kann ich mehrere Anträge stellen?',
                    a: 'Ja, Sie können für unterschiedliche Projekte mehrere Anträge einreichen. Pro Projekt ist jedoch nur ein Antrag möglich.'
                  },
                  {
                    q: 'Ist eine Ko-Finanzierung erforderlich?',
                    a: 'Bei den meisten Programmen ist ein Eigenanteil von 10-20% erforderlich. Dieser kann auch durch Eigenleistungen erbracht werden.'
                  },
                  {
                    q: 'Wann erhalte ich eine Rückmeldung?',
                    a: 'Die Bearbeitungsdauer beträgt in der Regel 6-8 Wochen nach Einreichung. Sie erhalten eine schriftliche Zu- oder Absage.'
                  },
                  {
                    q: 'Kann ich den Antrag nach Einreichung noch ändern?',
                    a: 'Kleinere Änderungen sind in Absprache mit dem Fördergeber möglich. Größere Änderungen erfordern einen neuen Antrag.'
                  },
                  {
                    q: 'Was passiert bei Ablehnung?',
                    a: 'Sie erhalten eine Begründung und können in der nächsten Förderrunde einen überarbeiteten Antrag einreichen.'
                  }
                ].map((faq, i) => (
                  <div key={i} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <h3 className="font-bold text-gray-900 mb-2">{faq.q}</h3>
                    <p className="text-gray-600">{faq.a}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <aside className="space-y-6 lg:sticky lg:top-28">
          <div className="glass-surface rounded-3xl p-5">
            <h3 className="text-lg font-semibold text-brand-navy">Bereit zum Beantragen?</h3>
            <p className="mt-2 text-sm text-slate-600">
              Starten Sie jetzt Ihre KI-gestützte Antragstellung oder exportieren Sie die Informationen für Ihr Team.
            </p>
            <div className="mt-4 space-y-3">
              <button onClick={handleApplyWithAI} disabled={applying} className="btn-primary w-full">
                <Sparkles size={18} />
                <span>{applying ? 'Wird erstellt…' : 'Jetzt beantragen'}</span>
              </button>
              <button onClick={() => window.print()} className="btn-secondary w-full text-sm">
                Ausschreibung drucken
              </button>
              <button
                onClick={handleExportDocx}
                disabled={exporting}
                className="btn-secondary w-full text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {exporting ? (
                  <>
                    <div className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white"></div>
                    Exportiere...
                  </>
                ) : (
                  <>
                    <Download size={18} />
                    Als DOCX exportieren
                  </>
                )}
              </button>
            </div>
          </div>

          {funding.tags && funding.tags.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-brand-navy">Kategorien</h3>
              <div className="mt-3 flex flex-wrap gap-2">
                {funding.tags.map((tag, index) => (
                  <span key={index} className="badge-soft text-xs">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {funding.source_url && (
            <div className="card">
              <h3 className="text-sm font-semibold text-brand-navy">Offizielle Quelle</h3>
              <a
                href={funding.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-2 inline-flex items-center gap-2 text-sm font-semibold text-brand-navy transition-colors hover:text-brand-green"
              >
                <ExternalLink size={16} /> Zur Ausschreibung
              </a>
            </div>
          )}

          {funding.scraped_at && (
            <div className="card surface-muted">
              <h3 className="text-sm font-semibold text-brand-navy">Zuletzt aktualisiert</h3>
              <p className="mt-2 text-sm text-slate-500">
                {new Date(funding.scraped_at).toLocaleDateString('de-DE', {
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric',
                })}
              </p>
            </div>
          )}

          <InfoBox variant="info" title="Support" icon={HelpCircle}>
            <div className="space-y-2 text-sm">
              <p>Unser Team begleitet Sie gern bei individuellen Fragen.</p>
              <div className="space-y-1">
                <a href="mailto:support@edufunds.de" className="text-brand-navy underline decoration-brand-green/50 decoration-2 underline-offset-4">
                  support@edufunds.de
                </a>
                <p className="text-brand-navy/80">+49 30 123 456 789</p>
              </div>
            </div>
          </InfoBox>
        </aside>
      </div>
    </div>
  )
}

export default FundingDetailPage

