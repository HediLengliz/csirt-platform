import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { incidentsApi } from '../lib/api'
import { useToastContext } from '../hooks/useToastContext'
import QuickActions from '../components/QuickActions'
import { ArrowLeft, Edit, Save, Tag, Shield, FileDown } from 'lucide-react'
import { format } from 'date-fns'
import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { exportToPDF } from '../utils/pdfExport'

export default function IncidentDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { success, error } = useToastContext()
  const [isEditing, setIsEditing] = useState(false)
  const pdfContentRef = useRef<HTMLDivElement>(null)

  const { data: incident, isLoading } = useQuery({
    queryKey: ['incidents', id],
    queryFn: () => incidentsApi.getById(Number(id)).then((res) => res.data),
    enabled: !!id,
  })

  const updateMutation = useMutation({
    mutationFn: (update: any) => incidentsApi.update(Number(id!), update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
      queryClient.invalidateQueries({ queryKey: ['incidents', id] })
      success('Incident updated successfully')
      setIsEditing(false)
    },
    onError: (err: any) => {
      error(err.response?.data?.detail || 'Failed to update incident')
    },
  })

  const [editData, setEditData] = useState({
    title: '',
    description: '',
    severity: '',
    status: '',
    assigned_to: '',
  })

  // Initialize editData when incident loads
  useEffect(() => {
    if (incident) {
      setEditData((prev) => {
        // Only update if title is empty (initial state)
        if (!prev.title || prev.title === '') {
          return {
            title: incident.title,
            description: incident.description || '',
            severity: incident.severity,
            status: incident.status,
            assigned_to: incident.assigned_to || '',
          }
        }
        return prev
      })
    }
  }, [incident])

  // Handle loading state
  if (isLoading) {
    return <div className="card text-center py-8">Loading...</div>
  }

  // Handle no incident found
  if (!incident) {
    return <div className="card text-center py-8">Incident not found</div>
  }

  const severityColors = {
    critical: 'badge-critical',
    high: 'badge-high',
    medium: 'badge-medium',
    low: 'badge-low',
  }

  const handleUpdateStatus = (status: string) => {
    updateMutation.mutate({ status })
  }

  const handleSave = () => {
    updateMutation.mutate(editData)
  }

  const handleExportPDF = () => {
    if (!pdfContentRef.current || !incident) {
      error('Unable to export PDF')
      return
    }

    try {
      const filename = `incident-${incident.id}-${format(new Date(), 'yyyy-MM-dd')}.pdf`
      exportToPDF(pdfContentRef.current, filename)
      success('PDF export initiated. Use the print dialog to save as PDF.')
    } catch (err: any) {
      error(err.message || 'Failed to export PDF')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-slate-400 hover:text-white"
        >
          <ArrowLeft size={20} />
          Back
        </button>
        {!isEditing && incident && (
          <button onClick={handleExportPDF} className="btn btn-secondary">
            <FileDown size={18} className="mr-2" />
            Export PDF
          </button>
        )}
      </div>

      <div className="card" ref={pdfContentRef}>
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            {isEditing ? (
              <input
                type="text"
                value={editData.title}
                onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                className="input text-2xl font-bold mb-2"
              />
            ) : (
              <>
                <h1 className="text-3xl font-bold mb-2 text-white">{incident.title}</h1>
                <div className="flex items-center gap-2 mb-4">
                  <span className={`badge ${severityColors[incident.severity]}`}>
                    {incident.severity.toUpperCase()}
                  </span>
                  <span className="badge">{incident.status}</span>
                </div>
              </>
            )}
          </div>
          {!isEditing ? (
            <button
              onClick={() => setIsEditing(true)}
              className="btn btn-secondary"
            >
              <Edit size={18} className="mr-2" />
              Edit
            </button>
          ) : (
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setIsEditing(false)
                  setEditData({
                    title: incident.title,
                    description: incident.description || '',
                    severity: incident.severity,
                    status: incident.status,
                    assigned_to: incident.assigned_to || '',
                  })
                }}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={updateMutation.isPending}
                className="btn btn-primary"
              >
                <Save size={18} className="mr-2" />
                Save
              </button>
            </div>
          )}
        </div>

        {isEditing ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Description
              </label>
              <textarea
                value={editData.description}
                onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                className="input"
                rows={4}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Severity
                </label>
                <select
                  value={editData.severity}
                  onChange={(e) => setEditData({ ...editData, severity: e.target.value })}
                  className="input"
                >
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Status
                </label>
                <select
                  value={editData.status}
                  onChange={(e) => setEditData({ ...editData, status: e.target.value })}
                  className="input"
                >
                  <option value="open">Open</option>
                  <option value="investigating">Investigating</option>
                  <option value="contained">Contained</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Assigned To
              </label>
              <input
                type="text"
                value={editData.assigned_to}
                onChange={(e) => setEditData({ ...editData, assigned_to: e.target.value })}
                className="input"
                placeholder="Analyst name"
              />
            </div>
          </div>
        ) : (
          <>
            {incident.description && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">Description</h3>
                <p className="text-slate-300">{incident.description}</p>
              </div>
            )}

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="info-row">
                <span className="info-label">Assigned To:</span>
                <span className="info-value">{incident.assigned_to || 'Unassigned'}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Created:</span>
                <span className="info-value">
                  {format(new Date(incident.created_at), 'MMM dd, yyyy HH:mm')}
                </span>
              </div>
              {incident.updated_at && (
                <div className="info-row">
                  <span className="info-label">Updated:</span>
                  <span className="info-value">
                    {format(new Date(incident.updated_at), 'MMM dd, yyyy HH:mm')}
                  </span>
                </div>
              )}
              <div className="info-row">
                <span className="info-label">Status:</span>
                <span className="info-value capitalize">{incident.status}</span>
              </div>
            </div>

            {incident.alert_id && (
              <div className="mb-6 p-4 bg-slate-700/50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Shield size={18} className="text-blue-400" />
                  <span className="text-sm font-medium text-slate-300">Related Alert</span>
                </div>
                <Link
                  to={`/alerts/${incident.alert_id}`}
                  className="text-blue-400 hover:text-blue-300 text-sm"
                >
                  View Alert #{incident.alert_id} →
                </Link>
              </div>
            )}

            {incident.tags && incident.tags.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                  <Tag size={18} />
                  Tags
                </h3>
                <div className="flex flex-wrap gap-2">
                  {incident.tags.map((tag: string, index: number) => (
                    <span key={index} className="badge badge-info">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {incident.ioc && incident.ioc.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                  <Shield size={18} />
                  Indicators of Compromise (IOCs)
                </h3>
                <div className="space-y-2">
                  {incident.ioc.map((ioc: { type: string; value: string }, index: number) => (
                    <div
                      key={index}
                      className="flex items-center gap-2 p-2 bg-slate-700/50 rounded-lg"
                    >
                      <span className="badge badge-info">{ioc.type}</span>
                      <span className="text-sm text-slate-300">{ioc.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <QuickActions
              incident={incident}
              onUpdateStatus={handleUpdateStatus}
            />
          </>
        )}
      </div>
    </div>
  )
}
