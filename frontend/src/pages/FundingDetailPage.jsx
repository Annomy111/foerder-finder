import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { fundingAPI } from '@/services/api'

function FundingDetailPage() {
  const { fundingId } = useParams()
  const [funding, setFunding] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadFunding()
  }, [fundingId])

  const loadFunding = async () => {
    try {
      const data = await fundingAPI.getById(fundingId)
      setFunding(data)
    } catch (error) {
      console.error('Fehler:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Lädt...</div>
  if (!funding) return <div>Nicht gefunden</div>

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">{funding.title}</h1>
      <div className="card">
        <p className="whitespace-pre-wrap">{funding.cleaned_text}</p>
      </div>
    </div>
  )
}

export default FundingDetailPage
