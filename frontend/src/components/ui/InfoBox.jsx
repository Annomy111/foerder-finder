const variants = {
  info: 'bg-blue-50 border-blue-200 text-blue-800',
  success: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-700',
  warning: 'bg-amber-100 border-amber-300 text-amber-800',
  danger: 'bg-red-100 border-red-300 text-red-800',
}

const cx = (...classes) => classes.filter(Boolean).join(' ')

function InfoBox({ title, icon: Icon, variant = 'info', actions, children, className }) {
  return (
    <section
      className={cx(
        'rounded-2xl border px-4 py-3 sm:px-5 sm:py-4 shadow-sm animate-fade-in',
        variants[variant],
        className,
      )}
      role="status"
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          {Icon && (
            <span className="mt-0.5 inline-flex h-9 w-9 items-center justify-center rounded-2xl bg-white/60 text-current shadow-inner">
              <Icon size={18} strokeWidth={1.75} />
            </span>
          )}
          <div className="space-y-1">
            {title && <h3 className="font-semibold text-sm uppercase tracking-wide text-current/80">{title}</h3>}
            <div className="text-sm leading-relaxed text-current/90">{children}</div>
          </div>
        </div>
        {actions && <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div>}
      </div>
    </section>
  )
}

export default InfoBox
