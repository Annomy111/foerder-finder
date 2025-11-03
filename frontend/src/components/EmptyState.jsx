import { FileSearch } from 'lucide-react'

/**
 * Empty State Component
 */
function EmptyState({ icon: Icon = FileSearch, title, description, action }) {
  return (
    <div className="card animate-fade-in py-16 text-center">
      <div className="mb-6 flex justify-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-brand-navy/10">
          <Icon className="h-9 w-9 text-brand-navy/60" />
        </div>
      </div>
      <h3 className="mb-2 text-lg font-semibold text-brand-navy">{title}</h3>
      <p className="mx-auto mb-6 max-w-md text-slate-600">{description}</p>
      {action}
    </div>
  )
}

export default EmptyState
