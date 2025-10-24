import { FileSearch } from 'lucide-react'

/**
 * Empty State Component
 */
function EmptyState({ icon: Icon = FileSearch, title, description, action }) {
  return (
    <div className="card text-center py-16 animate-fade-in">
      <div className="flex justify-center mb-6">
        <div className="p-4 bg-gray-100 rounded-full">
          <Icon className="w-12 h-12 text-gray-400" />
        </div>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-6 max-w-md mx-auto">{description}</p>
      {action}
    </div>
  )
}

export default EmptyState
