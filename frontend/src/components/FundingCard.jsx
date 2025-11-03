import { Link } from 'react-router-dom'
import { Building2, Clock, Euro, MapPin, Calendar, ArrowRight, Sparkles } from 'lucide-react'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

// Helper function to get display title
function getDisplayTitle(funding) {
  if (!funding) return ''
  if (funding.title && funding.title !== 'Unbekannt') return funding.title
  if (funding.provider) return funding.provider
  return 'Förderprogramm'
}

/**
 * Modern Funding Card Component with shadcn/ui
 *
 * Features:
 * - shadcn/ui Card components
 * - Responsive design
 * - Hover animations
 * - Deadline warnings
 * - Funding amount badges
 * - Tags display
 */
export function FundingCard({ funding }) {
  const fundingId = funding.funding_id ?? funding.id ?? funding.uuid ?? funding.slug
  const daysUntilDeadline = funding.deadline
    ? Math.ceil((new Date(funding.deadline) - new Date()) / (1000 * 60 * 60 * 24))
    : null

  const isUrgent = daysUntilDeadline !== null && daysUntilDeadline > 0 && daysUntilDeadline < 7
  const hasDeadlinePassed = daysUntilDeadline !== null && daysUntilDeadline < 0

  // Extract funding amount info
  const hasFundingAmount = funding.min_funding_amount || funding.max_funding_amount
  const fundingAmountText = hasFundingAmount
    ? `${funding.min_funding_amount?.toLocaleString('de-DE') || '?'}${
        funding.max_funding_amount
          ? ` - ${funding.max_funding_amount.toLocaleString('de-DE')}`
          : '+'
      } €`
    : null

  // Extract description from cleaned_text (first 150 chars)
  const description = funding.cleaned_text
    ? funding.cleaned_text
        .replace(/^#.*$/gm, '') // Remove markdown headers
        .replace(/\n+/g, ' ') // Replace newlines with spaces
        .trim()
        .substring(0, 150) + '...'
    : null

  return (
    <Card className="group relative overflow-hidden transition-all hover:shadow-xl hover:-translate-y-1 duration-300">
      {/* Urgent Badge */}
      {isUrgent && (
        <div className="absolute right-4 top-4 z-10">
          <Badge variant="destructive" className="shadow-lg">
            <Clock className="mr-1 h-3 w-3" />
            Dringend
          </Badge>
        </div>
      )}

      {/* Gradient Overlay (subtle) */}
      <div className="absolute inset-0 bg-gradient-to-br from-brand-navy/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

      <CardHeader className="relative pb-4">
        <CardTitle className="text-xl font-bold leading-tight text-brand-navy group-hover:text-brand-green transition-colors line-clamp-2">
          {getDisplayTitle(funding)}
        </CardTitle>

        {/* Provider */}
        <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
          <Building2 className="h-4 w-4" />
          <span className="font-medium">{funding.provider || 'Keine Angabe'}</span>
        </div>
      </CardHeader>

      <CardContent className="relative space-y-4 pb-4">
        {/* Description */}
        {description && (
          <p className="text-sm text-muted-foreground leading-relaxed line-clamp-3">
            {description}
          </p>
        )}

        {/* Info Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {/* Deadline */}
          {funding.deadline && (
            <div className={`rounded-lg border p-3 ${
              isUrgent ? 'border-rose-200 bg-rose-50' :
              hasDeadlinePassed ? 'border-slate-200 bg-slate-50' :
              'border-slate-200 bg-slate-50'
            }`}>
              <div className="flex items-center gap-1.5 mb-1">
                <Calendar className={`h-3.5 w-3.5 ${
                  isUrgent ? 'text-rose-600' :
                  hasDeadlinePassed ? 'text-slate-400' :
                  'text-brand-navy'
                }`} />
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Frist
                </p>
              </div>
              <p className={`text-sm font-bold ${
                isUrgent ? 'text-rose-700' :
                hasDeadlinePassed ? 'text-slate-400' :
                'text-brand-navy'
              }`}>
                {new Date(funding.deadline).toLocaleDateString('de-DE', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric',
                })}
              </p>
              {daysUntilDeadline !== null && daysUntilDeadline > 0 && (
                <p className="text-xs font-medium text-muted-foreground mt-0.5">
                  Noch {daysUntilDeadline} Tage
                </p>
              )}
              {hasDeadlinePassed && (
                <p className="text-xs font-medium text-slate-400 mt-0.5">
                  Abgelaufen
                </p>
              )}
            </div>
          )}

          {/* Funding Amount */}
          {hasFundingAmount && (
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
              <div className="flex items-center gap-1.5 mb-1">
                <Euro className="h-3.5 w-3.5 text-emerald-600" />
                <p className="text-xs font-semibold uppercase tracking-wide text-emerald-700">
                  Fördersumme
                </p>
              </div>
              <p className="text-sm font-bold text-emerald-700">
                {fundingAmountText}
              </p>
            </div>
          )}

          {/* Region (if deadline/funding not available) */}
          {!funding.deadline && !hasFundingAmount && funding.region && (
            <div className="rounded-lg border border-blue-200 bg-blue-50 p-3">
              <div className="flex items-center gap-1.5 mb-1">
                <MapPin className="h-3.5 w-3.5 text-blue-600" />
                <p className="text-xs font-semibold uppercase tracking-wide text-blue-700">
                  Region
                </p>
              </div>
              <p className="text-sm font-bold text-blue-700">
                {funding.region}
              </p>
            </div>
          )}
        </div>

        {/* Tags */}
        {funding.tags && funding.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {funding.tags.slice(0, 3).map((tag, index) => (
              <Badge key={index} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
            {funding.tags.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{funding.tags.length - 3}
              </Badge>
            )}
          </div>
        )}
      </CardContent>

      <CardFooter className="relative pt-0">
        <Button
          asChild
          variant="ghost"
          className="w-full group/button hover:bg-brand-navy/5"
        >
          <Link to={fundingId ? `/funding/${fundingId}` : '#'}>
            <Sparkles className="mr-2 h-4 w-4 text-brand-green" />
            <span className="flex-1 text-left font-semibold text-brand-navy">
              Details & KI-Antrag
            </span>
            <ArrowRight className="h-4 w-4 text-brand-green transition-transform group-hover/button:translate-x-1" />
          </Link>
        </Button>
      </CardFooter>
    </Card>
  )
}

export default FundingCard
