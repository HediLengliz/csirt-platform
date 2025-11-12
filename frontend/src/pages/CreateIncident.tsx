import { useState, useEffect } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { incidentsApi, alertsApi } from '../lib/api'
import { useToastContext } from '../contexts/ToastContext'
import { Save, X, Plus, Trash2 } from 'lucide-react'

export default function CreateIncident() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const alertId = searchParams.get('alertId')
  const { success, error } = useToastContext()
  const queryClient = useQueryClient()

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    severity: 'medium',
    alert_id: alertId ? parseInt(alertId) : undefined,
    tags: [] as string[],
    ioc: [] as Array<{ type: string; value: string }>,
  })

  const [newTag, setNewTag] = useState('')
  const [newIoc, setNewIoc] = useState({ type: 'ip', value: '' })

  // Fetch alert data if alertId is provided
  const { data: alert } = useQuery({
    queryKey: ['alerts', alertId],
    queryFn: () => alertsApi.getById(Number(alertId!)).then((res) => res.data),
    enabled: !!alertId,
  })

  // Pre-fill form if alert exists
  useEffect(() => {
    if (alert && !formData.title) {
      setFormData({
        ...formData,
        title: `Incident: ${alert.title}`,
        description: alert.description || '',
        severity: alert.priority === 'critical' ? 'critical' : alert.priority === 'high' ? 'high' : 'medium',
        alert_id: alert.id,
      })
    }
  }, [alert])

  const mutation = useMutation({
    mutationFn: (data: any) => incidentsApi.create(data),
    onSuccess: (data) => {
      success('Incident created successfully')
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
      setTimeout(() => {
        navigate(`/incidents/${data.data.id}`)
      }, 1000)
    },
    onError: (err: any) => {
      error(err.response?.data?.detail || 'Failed to create incident')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(formData)
  }

  const addTag = () => {
    if (newTag && !formData.tags.includes(newTag)) {
      setFormData({ ...formData, tags: [...formData.tags, newTag] })
      setNewTag('')
    }
  }

  const removeTag = (tag: string) => {
    setFormData({ ...formData, tags: formData.tags.filter((t) => t !== tag) })
  }

  const addIoc = () => {
    if (newIoc.value && !formData.ioc.some((i) => i.value === newIoc.value)) {
      setFormData({ ...formData, ioc: [...formData.ioc, { ...newIoc }] })
      setNewIoc({ type: 'ip', value: '' })
    }
  }

  const removeIoc = (index: number) => {
    setFormData({ ...formData, ioc: formData.ioc.filter((_, i) => i !== index) })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Create Incident</h1>
        <p className="text-slate-400">
          {alertId ? `Create incident from alert #${alertId}` : 'Create a new security incident'}
        </p>
      </div>

      {alert && (
        <div className="card bg-blue-500/10 border-blue-500/20">
          <p className="text-sm text-blue-400 mb-2">Creating incident from alert:</p>
          <p className="font-semibold text-white">{alert.title}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Title *
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="input"
            placeholder="Incident title"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="input"
            rows={4}
            placeholder="Incident description..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Severity *
          </label>
          <select
            value={formData.severity}
            onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
            className="input"
            required
          >
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Tags
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
              className="input flex-1"
              placeholder="Add tag and press Enter"
            />
            <button
              type="button"
              onClick={addTag}
              className="btn btn-secondary"
            >
              <Plus size={18} />
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {formData.tags.map((tag) => (
              <span
                key={tag}
                className="badge badge-info flex items-center gap-1"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="hover:text-red-400"
                >
                  <X size={14} />
                </button>
              </span>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Indicators of Compromise (IOCs)
          </label>
          <div className="flex gap-2 mb-2">
            <select
              value={newIoc.type}
              onChange={(e) => setNewIoc({ ...newIoc, type: e.target.value })}
              className="input w-32"
            >
              <option value="ip">IP</option>
              <option value="domain">Domain</option>
              <option value="url">URL</option>
              <option value="hash">Hash</option>
              <option value="email">Email</option>
              <option value="file">File</option>
            </select>
            <input
              type="text"
              value={newIoc.value}
              onChange={(e) => setNewIoc({ ...newIoc, value: e.target.value })}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addIoc())}
              className="input flex-1"
              placeholder="IOC value"
            />
            <button
              type="button"
              onClick={addIoc}
              className="btn btn-secondary"
            >
              <Plus size={18} />
            </button>
          </div>
          <div className="space-y-2">
            {formData.ioc.map((ioc, index) => (
              <div
                key={index}
                className="flex items-center gap-2 p-2 bg-slate-700 rounded-lg"
              >
                <span className="badge badge-info">{ioc.type}</span>
                <span className="flex-1 text-sm text-slate-300">{ioc.value}</span>
                <button
                  type="button"
                  onClick={() => removeIoc(index)}
                  className="p-1 hover:text-red-400"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="flex gap-3 justify-end">
          <button
            type="button"
            onClick={() => navigate('/incidents')}
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
            {mutation.isPending ? 'Creating...' : 'Create Incident'}
          </button>
        </div>
      </form>
    </div>
  )
}

