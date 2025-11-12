import { MLDetectionResult, MLClassification } from '../lib/api'
import { Brain, AlertTriangle, Shield, Target, TrendingUp, Tag, Eye } from 'lucide-react'

interface MLInsightsProps {
  detectionResult?: MLDetectionResult
  classification?: MLClassification
  eventId?: number
}

export default function MLInsights({ detectionResult, classification, eventId }: MLInsightsProps) {
  const data = detectionResult || (classification ? {
    classification,
    is_anomaly: false,
    anomaly_score: 0,
    risk_level: classification.recommended_priority || 'low',
    recommended_action: 'monitor',
    ml_confidence: classification.confidence,
    event_id: eventId || 0,
  } : null)

  if (!data) {
    return null
  }

  const riskColors: { [key: string]: string } = {
    critical: 'bg-red-500/20 text-red-400 border-red-500/50',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    low: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
  }

  const actionColors: { [key: string]: string } = {
    isolate_and_contain: 'bg-red-500/20 text-red-400',
    block_and_investigate: 'bg-orange-500/20 text-orange-400',
    block_ip: 'bg-yellow-500/20 text-yellow-400',
    rate_limit: 'bg-blue-500/20 text-blue-400',
    investigate: 'bg-purple-500/20 text-purple-400',
    review: 'bg-gray-500/20 text-gray-400',
    monitor: 'bg-green-500/20 text-green-400',
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Brain size={20} className="text-blue-400" />
        <h3 className="text-lg font-semibold">ML Insights</h3>
      </div>

      {/* Anomaly Detection */}
      {detectionResult && (
        <div className="card p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <AlertTriangle size={18} className="text-yellow-400" />
              <span className="font-medium">Anomaly Detection</span>
            </div>
            <span className={`badge ${data.is_anomaly ? 'badge-critical' : 'badge-success'}`}>
              {data.is_anomaly ? 'Anomaly Detected' : 'Normal'}
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div>
              <p className="text-sm text-slate-400">Anomaly Score</p>
              <p className="text-lg font-bold">{(data.anomaly_score * 100).toFixed(1)}%</p>
            </div>
            <div className="flex-1">
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${data.is_anomaly ? 'bg-red-500' : 'bg-green-500'}`}
                  style={{ width: `${data.anomaly_score * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Classification */}
      {data.classification && (
        <div className="card p-4">
          <div className="flex items-center gap-2 mb-3">
            <Shield size={18} className="text-blue-400" />
            <span className="font-medium">Classification</span>
          </div>
          
          {data.classification.attack_type && (
            <div className="mb-3">
              <p className="text-sm text-slate-400 mb-1">Attack Type</p>
              <span className="badge badge-critical text-sm">
                {data.classification.attack_type.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4 mb-3">
            <div>
              <p className="text-sm text-slate-400 mb-1">Confidence</p>
              <p className="text-lg font-bold">{(data.classification.confidence * 100).toFixed(1)}%</p>
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-1">Category</p>
              <p className="text-sm font-medium capitalize">{data.classification.category}</p>
            </div>
          </div>

          {data.classification.tags && data.classification.tags.length > 0 && (
            <div className="mb-3">
              <p className="text-sm text-slate-400 mb-2 flex items-center gap-1">
                <Tag size={14} />
                Tags
              </p>
              <div className="flex flex-wrap gap-2">
                {data.classification.tags.map((tag, idx) => (
                  <span key={idx} className="badge badge-info text-xs">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {data.classification.ioc && data.classification.ioc.length > 0 && (
            <div>
              <p className="text-sm text-slate-400 mb-2 flex items-center gap-1">
                <Eye size={14} />
                Indicators of Compromise ({data.classification.ioc.length})
              </p>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {data.classification.ioc.slice(0, 5).map((ioc, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs bg-slate-700/50 p-2 rounded">
                    <span className="badge badge-info text-xs">{ioc.type}</span>
                    <span className="text-slate-300 font-mono">{ioc.value}</span>
                  </div>
                ))}
                {data.classification.ioc.length > 5 && (
                  <p className="text-xs text-slate-400">+{data.classification.ioc.length - 5} more</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Risk Level & Recommended Action */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className={`card p-4 border ${riskColors[data.risk_level] || riskColors.low}`}>
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={18} />
            <span className="font-medium">Risk Level</span>
          </div>
          <p className="text-2xl font-bold capitalize">{data.risk_level}</p>
        </div>

        <div className={`card p-4 ${actionColors[data.recommended_action] || actionColors.monitor}`}>
          <div className="flex items-center gap-2 mb-2">
            <Target size={18} />
            <span className="font-medium">Recommended Action</span>
          </div>
          <p className="text-sm font-medium capitalize">
            {data.recommended_action.replace('_', ' ')}
          </p>
        </div>
      </div>

      {/* ML Confidence */}
      <div className="card p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain size={18} className="text-purple-400" />
            <span className="font-medium">ML Confidence</span>
          </div>
          <span className="text-lg font-bold">{(data.ml_confidence * 100).toFixed(1)}%</span>
        </div>
        <div className="mt-2 w-full bg-slate-700 rounded-full h-2">
          <div
            className="bg-purple-500 h-2 rounded-full"
            style={{ width: `${data.ml_confidence * 100}%` }}
          />
        </div>
      </div>
    </div>
  )
}
