import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { applicationsAPI, draftsAPI, fundingAPI } from '@/services/api'
import {
  Sparkles,
  FileText,
  Download,
  Trash2,
  ChevronLeft,
  Loader2,
  AlertCircle,
  ClipboardList,
  CheckCircle2,
  MessageCircle,
  Clock,
} from 'lucide-react'
import LoadingSpinner from '@/components/LoadingSpinner'
import ReactMarkdown from 'react-markdown'
import InfoBox from '@/components/ui/InfoBox'
import DismissibleBanner from '@/components/ui/DismissibleBanner'

function ApplicationDetailPage() {
  const { applicationId } = useParams()
  const navigate = useNavigate()

  const [application, setApplication] = useState(null)
  const [funding, setFunding] = useState(null)
  const [drafts, setDrafts] = useState([])
  const [selectedDraft, setSelectedDraft] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)

  // Draft Generation Form
  const [userQuery, setUserQuery] = useState('')
  const [showGenerator, setShowGenerator] = useState(true)

  useEffect(() => {
    let isMounted = true

    const fetchApplication = async () => {
      try {
        setLoading(true)
        const appData = await applicationsAPI.getById(applicationId)
        if (!isMounted) return
        setApplication(appData)

        if (appData.funding_id) {
          const fundingData = await fundingAPI.getById(appData.funding_id)
          if (isMounted) {
            setFunding(fundingData)
          }
        }

        const draftsData = await draftsAPI.getForApplication(applicationId)
        if (!isMounted) return
        setDrafts(draftsData)

        if (draftsData.length > 0) {
          setSelectedDraft(draftsData[0])
          setShowGenerator(false)
        }
      } catch (err) {
        if (isMounted) {
          console.error('Error loading application:', err)
          setError('Fehler beim Laden des Antrags')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchApplication()

    return () => {
      isMounted = false
    }
  }, [applicationId])

  const handleGenerateDraft = async () => {
    if (!userQuery.trim()) {
      setError('Bitte beschreiben Sie Ihre Projektidee')
      return
    }

    try {
      setGenerating(true)
      setError(null)

      const draft = await draftsAPI.generate({
        application_id: applicationId,
        funding_id: application.funding_id,
        user_query: userQuery,
      })

      // Reload drafts and select the new one
      const updatedDrafts = await draftsAPI.getForApplication(applicationId)
      setDrafts(updatedDrafts)
      setSelectedDraft(draft)
      setShowGenerator(false)
    } catch (err) {
      console.error('Error generating draft:', err)
      setError('Fehler beim Generieren des Entwurfs. Bitte versuchen Sie es erneut.')
    } finally {
      setGenerating(false)
    }
  }

  const handleDownloadDraft = () => {
    if (!selectedDraft) return

    const blob = new Blob([selectedDraft.generated_content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `foerderantrag-${application.title.substring(0, 30)}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleDeleteApplication = async () => {
    if (!confirm('Möchten Sie diesen Antrag wirklich löschen?')) return

    try {
      await applicationsAPI.delete(applicationId)
      navigate('/applications')
    } catch (err) {
      console.error('Error deleting application:', err)
      setError('Fehler beim Löschen des Antrags')
    }
  }

  if (loading) {
    return <LoadingSpinner text="Antrag wird geladen..." />
  }

  if (!application) {
    return (
      <div className="space-y-6">
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-center space-x-3">
            <AlertCircle className="text-red-600" size={24} />
            <div>
              <h3 className="font-semibold text-red-900">Antrag nicht gefunden</h3>
              <p className="text-sm text-red-700">Der angeforderte Antrag existiert nicht.</p>
            </div>
          </div>
        </div>
        <Link to="/applications" className="btn-secondary inline-flex items-center space-x-2">
          <ChevronLeft size={20} />
          <span>Zurück zur Übersicht</span>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-3">
          <Link to="/applications" className="inline-flex items-center gap-1 text-sm font-semibold text-brand-navy hover:text-brand-green">
            <ChevronLeft size={18} /> Zurück zur Übersicht
          </Link>
          <h1 className="text-3xl font-semibold text-brand-navy">{application.title}</h1>
          {funding && (
            <p className="text-sm text-slate-500">
              Förderprogramm: <span className="font-semibold text-brand-navy">{funding.title}</span>
            </p>
          )}
          <div className="flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            <span className="badge-soft">Status: {application.status}</span>
            <span className="badge-soft">KI-Unterstützt</span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {selectedDraft && (
            <button onClick={handleDownloadDraft} className="btn-secondary">
              <Download size={18} />
              <span>Als Markdown speichern</span>
            </button>
          )}
          {application.status === 'draft' && (
            <button onClick={handleDeleteApplication} className="btn-secondary text-red-600 hover:bg-red-50">
              <Trash2 size={18} />
              <span>Antrag löschen</span>
            </button>
          )}
        </div>
      </div>

      <DismissibleBanner id="application-guide">
        {({ close }) => (
          <div className="glass-surface flex flex-col gap-4 rounded-3xl px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3 text-brand-navy">
              <span className="mt-1 inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-navy/10">
                <ClipboardList size={20} />
              </span>
              <div className="space-y-1">
                <h2 className="text-base font-semibold">So funktioniert EduFunds Drafts</h2>
                <p className="text-sm text-slate-600">
                  Beschreiben Sie Ihre Idee, lassen Sie die KI einen strukturierten Entwurf generieren und finalisieren Sie den Antrag direkt hier im Workspace.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button onClick={() => setShowGenerator(true)} className="btn-secondary text-sm">
                Neue Idee einreichen
              </button>
              <button onClick={close} className="btn-ghost text-xs uppercase tracking-wide text-slate-500">
                Ausblenden
              </button>
            </div>
          </div>
        )}
      </DismissibleBanner>

      {error && (
        <InfoBox variant="danger" title="Fehler" icon={AlertCircle}>
          {error}
        </InfoBox>
      )}

      {/* Main Content Area */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-1">
          {showGenerator ? (
            <div className="card">
              <div className="mb-4 flex items-center gap-3">
                <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-navy/10">
                  <Sparkles size={22} className="text-brand-green" />
                </span>
                <div>
                  <h2 className="text-xl font-semibold text-brand-navy">KI-Entwurf erstellen</h2>
                  <p className="text-sm text-slate-500">Beschreiben Sie Ihre Projektidee</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="label">Projektbeschreibung</label>
                  <textarea
                    className="input min-h-[200px]"
                    placeholder="Beschreiben Sie Ihr Projekt: Ziele, Nutzen und Besonderheiten."
                    value={userQuery}
                    onChange={(e) => setUserQuery(e.target.value)}
                    disabled={generating}
                  />
                  <p className="mt-2 text-xs text-slate-500">
                    Je detaillierter Ihre Beschreibung, desto passgenauer wird der Entwurf.
                  </p>
                </div>

                <button
                  onClick={handleGenerateDraft}
                  disabled={generating || !userQuery.trim()}
                  className="btn-primary w-full"
                >
                  {generating ? (
                    <>
                      <Loader2 className="animate-spin" size={20} />
                      <span>Entwurf wird generiert…</span>
                    </>
                  ) : (
                    <>
                      <Sparkles size={20} />
                      <span>Entwurf generieren</span>
                    </>
                  )}
                </button>

                {drafts.length > 0 && (
                  <button onClick={() => { setShowGenerator(false); setSelectedDraft(drafts[0]) }} className="btn-secondary w-full">
                    Vorherige Entwürfe öffnen
                  </button>
                )}
              </div>

              <InfoBox variant="info" title="KI-Unterstützung" icon={Sparkles} className="mt-6">
                Professionelle Struktur, automatische Formatierung und Inspiration aus erfolgreichen Anträgen.
              </InfoBox>
            </div>
          ) : (
            <div className="card">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-brand-navy">Entwürfe ({drafts.length})</h2>
                <button onClick={() => setShowGenerator(true)} className="btn-secondary text-sm">
                  Neuer Entwurf
                </button>
              </div>
              <div className="mt-4 space-y-3">
                {drafts.map((draft, index) => {
                  const isActive = selectedDraft?.draft_id === draft.draft_id
                  return (
                    <button
                      key={draft.draft_id}
                      onClick={() => setSelectedDraft(draft)}
                      className={`w-full rounded-2xl border px-4 py-3 text-left transition-all ${
                        isActive
                          ? 'border-brand-navy/40 bg-brand-navy/5 shadow-soft'
                          : 'border-brand-navy/10 hover:border-brand-green/30 hover:bg-white'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-sm font-semibold text-brand-navy">
                          <FileText size={18} /> Entwurf {index + 1}
                        </div>
                        {draft.model_used && (
                          <span className="text-xs uppercase tracking-wide text-slate-500">
                            {draft.model_used}
                          </span>
                        )}
                      </div>
                      <p className="mt-1 text-xs text-slate-500">
                        Erstellt: {new Date(draft.created_at).toLocaleString('de-DE')}
                      </p>
                    </button>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-6 lg:col-span-2">
          <InfoBox variant="info" title="Bearbeitungsverlauf" icon={Clock}>
            <div className="flex flex-wrap items-center gap-4 text-xs uppercase tracking-wide text-slate-500">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={16} className="text-brand-green" /> Entwurf erstellt
              </div>
              <div className="flex items-center gap-2">
                <MessageCircle size={16} className="text-brand-navy" /> Kommentare folgen demnächst
              </div>
            </div>
          </InfoBox>

          {selectedDraft ? (
            <div className="card">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <h2 className="text-2xl font-semibold text-brand-navy">Antragsentwurf</h2>
                <span className="text-xs uppercase tracking-wide text-slate-400">
                  Generiert am {new Date(selectedDraft.created_at).toLocaleString('de-DE')}
                </span>
              </div>

              <div className="prose prose-lg max-w-none text-slate-700">
                <ReactMarkdown>{selectedDraft.generated_content}</ReactMarkdown>
              </div>

              <div className="mt-8 flex flex-col gap-4 border-t border-brand-navy/10 pt-6 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-sm text-slate-500">
                  Bitte prüfen Sie den Entwurf sorgfältig und ergänzen Sie schulische Besonderheiten vor der Einreichung.
                </p>
                <button onClick={handleDownloadDraft} className="btn-secondary">
                  <Download size={18} />
                  <span>Markdown exportieren</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="card bg-gray-50 border-gray-200">
              <div className="text-center py-12">
                <Sparkles className="mx-auto text-gray-400 mb-4" size={48} />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  Noch kein Entwurf vorhanden
                </h3>
                <p className="text-gray-600 mb-6">
                  Beschreiben Sie Ihre Projektidee, um einen KI-generierten Antragsentwurf zu erstellen.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ApplicationDetailPage
