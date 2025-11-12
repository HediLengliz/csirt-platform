import { Alert, Incident } from '../lib/api'
import { Link } from 'react-router-dom'
import { FileText, Send, CheckCircle, XCircle } from 'lucide-react'

interface QuickActionsProps {
  alert?: Alert
  incident?: Incident
  onUpdateStatus?: (status: string) => void
  onSendToIntegrations?: () => void
}

export default function QuickActions({ alert, incident, onUpdateStatus, onSendToIntegrations }: QuickActionsProps) {
  if (alert) {
    return (
      <div className="flex flex-wrap gap-1">
        {alert.status === 'new' && (
          <>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onUpdateStatus?.('in_progress')
              }}
              className="btn btn-primary text-xs px-2 py-1"
              title="Mark as In Progress"
            >
              <CheckCircle size={14} className="mr-1" />
              In Progress
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onUpdateStatus?.('resolved')
              }}
              className="btn btn-success text-xs px-2 py-1"
              title="Resolve Alert"
            >
              <CheckCircle size={14} className="mr-1" />
              Resolve
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onUpdateStatus?.('false_positive')
              }}
              className="btn btn-secondary text-xs px-2 py-1"
              title="Mark as False Positive"
            >
              <XCircle size={14} className="mr-1" />
              False Positive
            </button>
          </>
        )}
        <Link
          to={`/incidents/new?alertId=${alert.id}`}
          onClick={(e) => e.stopPropagation()}
          className="btn btn-primary text-xs px-2 py-1"
          title="Create Incident"
        >
          <FileText size={14} className="mr-1" />
          Incident
        </Link>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onSendToIntegrations?.()
          }}
          className="btn btn-secondary text-xs px-2 py-1"
          title="Send to Integrations"
        >
          <Send size={14} className="mr-1" />
          Send
        </button>
      </div>
    )
  }

  if (incident) {
    return (
      <div className="flex flex-wrap gap-2">
        {incident.status === 'open' && (
          <button
            onClick={() => onUpdateStatus?.('investigating')}
            className="btn btn-primary text-sm"
          >
            <CheckCircle size={16} className="mr-1" />
            Start Investigating
          </button>
        )}
        {incident.status === 'investigating' && (
          <button
            onClick={() => onUpdateStatus?.('contained')}
            className="btn btn-success text-sm"
          >
            <CheckCircle size={16} className="mr-1" />
            Mark Contained
          </button>
        )}
        {incident.status === 'contained' && (
          <button
            onClick={() => onUpdateStatus?.('resolved')}
            className="btn btn-success text-sm"
          >
            <CheckCircle size={16} className="mr-1" />
            Resolve
          </button>
        )}
      </div>
    )
  }

  return null
}

