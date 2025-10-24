import { useParams } from 'react-router-dom'

function ApplicationDetailPage() {
  const { applicationId } = useParams()

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Antrags-Details</h1>
      <div className="card">
        <p>Application ID: {applicationId}</p>
        <p className="text-gray-500 mt-4">TODO: Vollständige Implementierung mit KI-Entwurfsgenerator</p>
      </div>
    </div>
  )
}

export default ApplicationDetailPage
