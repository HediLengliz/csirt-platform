import { Link } from 'react-router-dom'
import { AlertTriangle, Clock } from 'lucide-react'
import { Alert } from '../lib/api'
import { formatDistanceToNow } from 'date-fns'

interface AlertCardProps {
  alert: Alert
}

export default function AlertCard({ alert }: AlertCardProps) {
  const priorityColors = {
    critical: 'badge-critical',
    high: 'badge-high',
    medium: 'badge-medium',
    low: 'badge-low',
    info: 'badge-info',
  }

  const statusColors = {
    new: 'bg-blue-500/20 text-blue-400',
    in_progress: 'bg-yellow-500/20 text-yellow-400',
    resolved: 'bg-green-500/20 text-green-400',
    false_positive: 'bg-gray-500/20 text-gray-400',
    ignored: 'bg-gray-500/20 text-gray-400',
  }

  return (
    <Link to={`/alerts/${alert.id}`}>
      <div className="card hover:bg-slate-700 transition-colors cursor-pointer">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500/10 rounded-lg">
              <AlertTriangle size={20} className="text-red-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white">{alert.title}</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className={`badge ${priorityColors[alert.priority]}`}>
                  {alert.priority.toUpperCase()}
                </span>
                <span className={`badge ${statusColors[alert.status]}`}>
                  {alert.status.replace('_', ' ')}
                </span>
              </div>
            </div>
          </div>
        </div>

        {alert.description && (
          <p className="text-sm text-slate-300 mb-3 line-clamp-2">{alert.description}</p>
        )}

        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-1">
            <Clock size={14} />
            <span>{formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}</span>
          </div>
          {alert.ml_score && (
            <span className="text-slate-500">ML Score: {(alert.ml_score * 100).toFixed(0)}%</span>
          )}
        </div>
      </div>
    </Link>
  )
}

