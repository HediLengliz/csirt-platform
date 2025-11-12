import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { eventsApi } from '../lib/api'
import { useToastContext } from '../contexts/ToastContext'
import { Save, X } from 'lucide-react'

export default function CreateEvent() {
  const navigate = useNavigate()
  const { success, error } = useToastContext()
  const queryClient = useQueryClient()

  const [formData, setFormData] = useState({
    source: 'custom',
    event_type: 'suspicious_activity',
    raw_data: {},
    timestamp: new Date().toISOString().slice(0, 16),
    source_ip: '',
    destination_ip: '',
    user: '',
    hostname: '',
    description: '',
    severity_score: '',
  })

  const mutation = useMutation({
    mutationFn: (data: any) => eventsApi.create(data),
    onSuccess: () => {
      success('Event created successfully')
      queryClient.invalidateQueries({ queryKey: ['events'] })
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      setTimeout(() => {
        navigate('/events')
      }, 1000)
    },
    onError: (err: any) => {
      error(err.response?.data?.detail || 'Failed to create event')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const data = {
      ...formData,
      raw_data: formData.raw_data || {},
      timestamp: formData.timestamp ? new Date(formData.timestamp).toISOString() : undefined,
      severity_score: formData.severity_score || undefined,
    }
    mutation.mutate(data)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Create Event</h1>
        <p className="text-slate-400">Create a new security event</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Source *
            </label>
            <select
              value={formData.source}
              onChange={(e) => setFormData({ ...formData, source: e.target.value })}
              className="input"
              required
            >
              <option value="custom">Custom</option>
              <option value="splunk">Splunk</option>
              <option value="elastic">Elastic</option>
              <option value="endpoint">Endpoint</option>
              <option value="network">Network</option>
              <option value="firewall">Firewall</option>
              <option value="ids_ips">IDS/IPS</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Event Type *
            </label>
            <select
              value={formData.event_type}
              onChange={(e) => setFormData({ ...formData, event_type: e.target.value })}
              className="input"
              required
            >
              <option value="suspicious_activity">Suspicious Activity</option>
              <option value="malware_detected">Malware Detected</option>
              <option value="unauthorized_access">Unauthorized Access</option>
              <option value="data_exfiltration">Data Exfiltration</option>
              <option value="brute_force">Brute Force</option>
              <option value="ddos">DDoS</option>
              <option value="phishing">Phishing</option>
              <option value="login_failure">Login Failure</option>
              <option value="login_success">Login Success</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Source IP
            </label>
            <input
              type="text"
              value={formData.source_ip}
              onChange={(e) => setFormData({ ...formData, source_ip: e.target.value })}
              className="input"
              placeholder="192.168.1.100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Destination IP
            </label>
            <input
              type="text"
              value={formData.destination_ip}
              onChange={(e) => setFormData({ ...formData, destination_ip: e.target.value })}
              className="input"
              placeholder="192.168.1.200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              User
            </label>
            <input
              type="text"
              value={formData.user}
              onChange={(e) => setFormData({ ...formData, user: e.target.value })}
              className="input"
              placeholder="username"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Hostname
            </label>
            <input
              type="text"
              value={formData.hostname}
              onChange={(e) => setFormData({ ...formData, hostname: e.target.value })}
              className="input"
              placeholder="hostname"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Severity Score
            </label>
            <input
              type="number"
              min="0"
              max="10"
              step="0.1"
              value={formData.severity_score}
              onChange={(e) => setFormData({ ...formData, severity_score: e.target.value })}
              className="input"
              placeholder="7.5"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Timestamp
            </label>
            <input
              type="datetime-local"
              value={formData.timestamp}
              onChange={(e) => setFormData({ ...formData, timestamp: e.target.value })}
              className="input"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Description *
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="input"
            rows={4}
            placeholder="Event description..."
            required
          />
        </div>

        <div className="flex gap-3 justify-end">
          <button
            type="button"
            onClick={() => navigate('/events')}
            className="btn btn-secondary"
          >
            <X size={18} className="mr-2" />
            Cancel
          </button>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="btn btn-primary"
          >
            <Save size={18} className="mr-2" />
            {mutation.isPending ? 'Creating...' : 'Create Event'}
          </button>
        </div>
      </form>
    </div>
  )
}

