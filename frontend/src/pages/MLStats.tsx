import { useQuery } from '@tanstack/react-query'
import { mlApi } from '../lib/api'
import { Brain, Activity, Shield, TrendingUp } from 'lucide-react'

export default function MLStats() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['ml-stats'],
    queryFn: () => mlApi.getStats().then((res) => res.data),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  if (isLoading) {
    return (
      <div className="card text-center py-8">
        <p className="text-slate-400">Loading ML statistics...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">ML System Statistics</h1>
        <p className="text-slate-400">Real-time machine learning system status and metrics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Anomaly Detector Status */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Brain size={24} className="text-blue-400" />
              <span className="font-semibold">Anomaly Detector</span>
            </div>
            <span className={`badge ${stats?.anomaly_detector_trained ? 'badge-success' : 'badge-warning'}`}>
              {stats?.anomaly_detector_trained ? 'Trained' : 'Not Trained'}
            </span>
          </div>
          <p className="text-sm text-slate-400">
            {stats?.anomaly_detector_trained
              ? 'Model is trained and ready for anomaly detection'
              : 'Model needs training data. Use update-models endpoint to train.'}
          </p>
        </div>

        {/* Events in Window */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Activity size={24} className="text-green-400" />
              <span className="font-semibold">Events in Window</span>
            </div>
            <span className="text-2xl font-bold">{stats?.events_in_window || 0}</span>
          </div>
          <p className="text-sm text-slate-400">
            Events currently in the ML processing window (last 100 events)
          </p>
        </div>

        {/* Patterns Loaded */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Shield size={24} className="text-purple-400" />
              <span className="font-semibold">Attack Patterns</span>
            </div>
            <span className="text-2xl font-bold">{stats?.patterns_loaded || 0}</span>
          </div>
          <p className="text-sm text-slate-400">
            Attack patterns loaded and ready for classification
          </p>
        </div>
      </div>

      {/* System Information */}
      <div className="card p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <TrendingUp size={20} />
          System Information
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-slate-400 mb-1">ML System Status</p>
            <p className="font-semibold text-green-400">Operational</p>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Processing Mode</p>
            <p className="font-semibold">Real-Time</p>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Detection Algorithm</p>
            <p className="font-semibold">Isolation Forest</p>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Classification Method</p>
            <p className="font-semibold">Pattern Matching + ML</p>
          </div>
        </div>
      </div>

      {/* Usage Instructions */}
      <div className="card p-6 bg-blue-500/10 border-blue-500/50">
        <h3 className="text-lg font-semibold mb-2 text-blue-400">How to Use</h3>
        <ul className="space-y-2 text-sm text-slate-300">
          <li>• ML insights are automatically displayed in alert details</li>
          <li>• Click "Refresh" on any alert to re-analyze with ML</li>
          <li>• Train the model using the API endpoint: <code className="bg-slate-700 px-2 py-1 rounded">POST /api/v1/ml/update-models</code></li>
          <li>• Minimum 10 events required for training</li>
        </ul>
      </div>
    </div>
  )
}

