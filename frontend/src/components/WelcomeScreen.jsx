import { Link } from 'react-router-dom'
import {
  Sparkles,
  TrendingUp,
  Clock,
  Award,
  ArrowRight,
  Search,
  FileText,
  Zap,
  CheckCircle2,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

/**
 * Welcome Screen Component
 *
 * Zeigt einen attraktiven Willkommensbildschirm mit:
 * - Hero Section mit CTA
 * - Feature Cards
 * - Quick Stats
 * - Login-Button
 */
export function WelcomeScreen() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-navy/5 via-white to-brand-green/5">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-brand-navy to-brand-navy/90">
        <div className="absolute inset-0 bg-grid-white/[0.05] bg-[size:20px_20px]" />
        <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8 lg:py-32">
          <div className="text-center">
            {/* Badge */}
            <Badge className="mb-6 bg-brand-green/20 text-brand-green hover:bg-brand-green/30">
              <Sparkles className="mr-1 h-3 w-3" />
              KI-gestützte Förderanträge
            </Badge>

            {/* Title */}
            <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl md:text-6xl">
              Fördermittel für Ihre
              <br />
              <span className="text-brand-green">Grundschule finden</span>
            </h1>

            {/* Subtitle */}
            <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-200">
              EduFunds durchsucht automatisch tausende Förderprogramme und erstellt mit KI maßgeschneiderte
              Anträge für Ihre Schule. Sparen Sie Zeit und erhöhen Sie Ihre Erfolgschancen.
            </p>

            {/* CTA Buttons */}
            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button asChild size="lg" className="bg-brand-green hover:bg-brand-green/90 text-white shadow-xl">
                <Link to="/login">
                  <Zap className="mr-2 h-5 w-5" />
                  Jetzt starten
                </Link>
              </Button>

              <Button asChild size="lg" variant="outline" className="bg-white/10 text-white border-white/20 hover:bg-white/20">
                <Link to="/funding">
                  <Search className="mr-2 h-5 w-5" />
                  Programme durchsuchen
                </Link>
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-sm text-slate-300">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-brand-green" />
                <span>Kostenlos für Grundschulen</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-brand-green" />
                <span>Datenschutz-konform (DSGVO)</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-brand-green" />
                <span>Keine versteckten Kosten</span>
              </div>
            </div>
          </div>
        </div>

        {/* Wave Divider */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg
            viewBox="0 0 1440 120"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="w-full"
          >
            <path
              d="M0 0L60 10C120 20 240 40 360 46.7C480 53 600 47 720 43.3C840 40 960 40 1080 46.7C1200 53 1320 67 1380 73.3L1440 80V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0V0Z"
              fill="white"
              fillOpacity="0.05"
            />
          </svg>
        </div>
      </div>

      {/* Features Section */}
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-brand-navy">
            So funktioniert EduFunds
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            In 3 einfachen Schritten zu Ihrer Förderung
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {/* Feature 1 */}
          <Card className="border-2 hover:border-brand-green/50 hover:shadow-xl transition-all duration-300">
            <CardHeader>
              <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-green/10">
                <Search className="h-7 w-7 text-brand-green" />
              </div>
              <CardTitle className="text-xl">1. Fördermittel finden</CardTitle>
              <CardDescription className="text-base">
                Durchsuchen Sie tausende aktuelle Förderprogramme speziell für Grundschulen
                in ganz Deutschland.
              </CardDescription>
            </CardHeader>
          </Card>

          {/* Feature 2 */}
          <Card className="border-2 hover:border-brand-green/50 hover:shadow-xl transition-all duration-300">
            <CardHeader>
              <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-green/10">
                <Sparkles className="h-7 w-7 text-brand-green" />
              </div>
              <CardTitle className="text-xl">2. KI-Antrag erstellen</CardTitle>
              <CardDescription className="text-base">
                Unsere KI analysiert Ihr Projekt und erstellt einen maßgeschneiderten,
                professionellen Förderantrag.
              </CardDescription>
            </CardHeader>
          </Card>

          {/* Feature 3 */}
          <Card className="border-2 hover:border-brand-green/50 hover:shadow-xl transition-all duration-300">
            <CardHeader>
              <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-green/10">
                <FileText className="h-7 w-7 text-brand-green" />
              </div>
              <CardTitle className="text-xl">3. Antrag einreichen</CardTitle>
              <CardDescription className="text-base">
                Überprüfen, anpassen und direkt einreichen. Fertig in Minuten statt Stunden!
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Stats Section */}
        <div className="mt-20 grid grid-cols-1 gap-8 sm:grid-cols-3">
          <div className="text-center">
            <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-navy/10 mb-4">
              <Award className="h-8 w-8 text-brand-navy" />
            </div>
            <div className="text-4xl font-bold text-brand-navy">52+</div>
            <div className="mt-2 text-sm text-muted-foreground">Aktive Förderprogramme</div>
          </div>

          <div className="text-center">
            <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-navy/10 mb-4">
              <TrendingUp className="h-8 w-8 text-brand-navy" />
            </div>
            <div className="text-4xl font-bold text-brand-navy">500K+</div>
            <div className="mt-2 text-sm text-muted-foreground">Euro Fördersumme verfügbar</div>
          </div>

          <div className="text-center">
            <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-navy/10 mb-4">
              <Clock className="h-8 w-8 text-brand-navy" />
            </div>
            <div className="text-4xl font-bold text-brand-navy">5 Min</div>
            <div className="mt-2 text-sm text-muted-foreground">Durchschn. Antragszeit</div>
          </div>
        </div>

        {/* Final CTA */}
        <div className="mt-20 text-center">
          <Card className="border-2 border-brand-green/20 bg-gradient-to-br from-brand-green/5 to-transparent">
            <CardContent className="p-12">
              <h3 className="text-2xl font-bold text-brand-navy mb-4">
                Bereit loszulegen?
              </h3>
              <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
                Melden Sie sich jetzt an und entdecken Sie, welche Fördermöglichkeiten
                auf Ihre Grundschule warten.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Button asChild size="lg" className="bg-brand-green hover:bg-brand-green/90 text-white">
                  <Link to="/login">
                    <Zap className="mr-2 h-5 w-5" />
                    Kostenlos registrieren
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link to="/funding">
                    Programme ansehen
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default WelcomeScreen
