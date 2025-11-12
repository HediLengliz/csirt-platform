import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertsApi, mlApi } from '../lib/api'
import { useToastContext } from '../contexts/ToastContext'
import QuickActions from '../components/QuickActions'
import MLInsights from '../components/MLInsights'
import { ArrowLeft, Link as LinkIcon, Brain, RefreshCw } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { Link } from 'react-router-dom'
import { useState } from 'react'

export default function AlertDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { success, error } = useToastContext()

  const { data: alert, isLoading } = useQuery({
    queryKey: ['alerts', id],
    queryFn: () => alertsApi.getById(Number(id)).then((res) => res.data),
    enabled: !!id,
  })

  const [mlDetectionResult, setMlDetectionResult] = useState<any>(null)
  const [isLoadingML, setIsLoadingML] = useState(false)

  // Fetch ML insights if event_id exists
  const { data: mlData, refetch: refetchML } = useQuery({
    queryKey: ['ml-detection', alert?.event_id],
    queryFn: () => {
      if (alert?.event_id) {
        return mlApi.detect(alert.event_id).then((res) => res.data)
      }
      return null
    },
    enabled: !!alert?.event_id,
  })

  const handleRefreshML = async () => {
    if (!alert?.event_id) return
    setIsLoadingML(true)
    try {
      const result = await mlApi.detect(alert.event_id)
      setMlDetectionResult(result.data)
      refetchML()
    } catch (err) {
      console.error('Error refreshing ML data:', err)
    } finally {
      setIsLoadingML(false)
    }
  }

  const updateMutation = useMutation({
    mutationFn: (update: any) => alertsApi.update(Number(id!), update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      queryClient.invalidateQueries({ queryKey: ['alerts', id] })
      success('Alert updated successfully')
    },
    onError: (err: any) => {
      error(err.response?.data?.detail || 'Failed to update alert')
    },
  })

  const sendMutation = useMutation({
    mutationFn: () => alertsApi.send(Number(id!)),
    onSuccess: () => {
      success('Alert sent to integrations')
    },
    onError: (err: any) => {
      error(err.response?.data?.detail || 'Failed to send alert')
    },
  })

  const handleUpdateStatus = (status: string) => {
    updateMutation.mutate({ status })
  }

  const handleSendToIntegrations = () => {
    sendMutation.mutate()
  }

  if (isLoading) {
    return <div className="card text-center py-8">Loading...</div>
  }

  if (!alert) {
    return <div className="card text-center py-8">Alert not found</div>
  }

  const priorityColors = {
    critical: 'badge-critical',
    high: 'badge-high',
    medium: 'badge-medium',
    low: 'badge-low',
    info: 'badge-info',
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-slate-400 hover:text-white"
      >
        <ArrowLeft size={20} />
        Back
      </button>

      <div className="card">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">{alert.title}</h1>
            <div className="flex items-center gap-2">
              <span className={`badge ${priorityColors[alert.priority]}`}>
                {alert.priority.toUpperCase()}
              </span>
              <span className="badge">{alert.status.replace('_', ' ')}</span>
            </div>
          </div>
        </div>

        {alert.description && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2">Description</h3>
            <p className="text-slate-300">{alert.description}</p>
          </div>
        )}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div>
            <p className="text-sm text-slate-400 mb-1">Source</p>
            <p className="font-semibold">{alert.source}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">ML Score</p>
            <p className="font-semibold">
              {alert.ml_score ? `${(alert.ml_score * 100).toFixed(0)}%` : 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Created</p>
            <p className="font-semibold">
              {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
            </p>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Status</p>
            <p className="font-semibold capitalize">{alert.status.replace('_', ' ')}</p>
          </div>
        </div>

        {alert.event_id && (
          <div className="mb-6 p-4 bg-slate-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <LinkIcon size={18} className="text-blue-400" />
              <span className="text-sm font-medium text-slate-300">Related Event</span>
            </div>
            <Link
              to={`/events/${alert.event_id}`}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              View Event #{alert.event_id} →
            </Link>
          </div>
        )}

        <QuickActions
          alert={alert}
          onUpdateStatus={handleUpdateStatus}
          onSendToIntegrations={handleSendToIntegrations}
        />
      </div>

      {/* ML Insights Section */}
      {alert.event_id && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">ML Analysis</h2>
            <button
              onClick={handleRefreshML}
              disabled={isLoadingML}
              className="btn btn-secondary text-sm"
            >
              <RefreshCw size={16} className={`mr-2 ${isLoadingML ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
          {mlData ? (
            <MLInsights detectionResult={mlData} />
          ) : mlDetectionResult ? (
            <MLInsights detectionResult={mlDetectionResult} />
          ) : (
            <div className="text-center py-8 text-slate-400">
              <Brain size={48} className="mx-auto mb-4 opacity-50" />
              <p>Click Refresh to analyze with ML</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

