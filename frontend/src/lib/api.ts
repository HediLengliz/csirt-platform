import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface Event {
  id: number
  source: string
  event_type: string
  timestamp?: string
  source_ip?: string
  destination_ip?: string
  user?: string
  hostname?: string
  description?: string
  created_at: string
}

export interface Alert {
  id: number
  title: string
  description?: string
  status: 'new' | 'in_progress' | 'resolved' | 'false_positive' | 'ignored'
  priority: 'critical' | 'high' | 'medium' | 'low' | 'info'
  ml_score?: number
  source: string
  event_id?: number
  created_at: string
}

export interface Incident {
  id: number
  title: string
  description?: string
  status: 'open' | 'investigating' | 'contained' | 'resolved' | 'closed'
  severity: 'critical' | 'high' | 'medium' | 'low'
  assigned_to?: string
  alert_id?: number
  tags?: string[]
  ioc?: Array<{ type: string; value: string }>
  created_at: string
  updated_at?: string
}

export interface AlertUpdate {
  status?: string
  notes?: string
}

export interface IncidentUpdate {
  title?: string
  description?: string
  status?: string
  severity?: string
  assigned_to?: string
  resolution_notes?: string
  tags?: string[]
  ioc?: Array<{ type: string; value: string }>
}

// ML System Interfaces
export interface MLClassification {
  category: string
  attack_type: string | null
  confidence: number
  tags: string[]
  recommended_priority: string | null
  ioc: Array<{ type: string; value: string }>
}

export interface MLDetectionResult {
  event_id: number
  is_anomaly: boolean
  anomaly_score: number
  classification: MLClassification
  risk_level: string
  recommended_action: string
  ml_confidence: number
}

export interface MLStats {
  anomaly_detector_trained: boolean
  events_in_window: number
  patterns_loaded: number
}

// Events API
export const eventsApi = {
  create: (event: Partial<Event>) => api.post<Event>('/events/', event),
  getAll: (params?: { skip?: number; limit?: number; source?: string; event_type?: string }) =>
    api.get<Event[]>('/events/', { params }),
  getById: (id: number) => api.get<Event>(`/events/${id}`),
}

// Alerts API
export const alertsApi = {
  getAll: (params?: { skip?: number; limit?: number; status?: string; priority?: string }) =>
    api.get<Alert[]>('/alerts/', { params }),
  getCritical: (limit: number = 50) => api.get<Alert[]>(`/alerts/critical?limit=${limit}`),
  getById: (id: number) => api.get<Alert>(`/alerts/${id}`),
  update: (id: number, update: AlertUpdate) => api.patch<Alert>(`/alerts/${id}`, update),
  send: (id: number) => api.post(`/alerts/${id}/send`),
}

// Incidents API
export const incidentsApi = {
  create: (incident: Partial<Incident>) => api.post<Incident>('/incidents/', incident),
  getAll: (params?: { skip?: number; limit?: number; status?: string; severity?: string }) =>
    api.get<Incident[]>('/incidents/', { params }),
  getById: (id: number) => api.get<Incident>(`/incidents/${id}`),
  update: (id: number, update: IncidentUpdate) => api.patch<Incident>(`/incidents/${id}`, update),
}

// Health API
export const healthApi = {
  check: () => axios.get('http://localhost:8000/health'),
}

// ML API
export const mlApi = {
  detect: (eventId: number) => api.post<MLDetectionResult>(`/ml/detect/${eventId}`),
  classify: (eventId: number) => api.post<{ event_id: number; classification: MLClassification }>(`/ml/classify/${eventId}`),
  getStats: () => api.get<MLStats>('/ml/stats'),
  updateModels: (eventIds: number[]) => api.post<{ status: string; events_used: number; message: string }>('/ml/update-models', eventIds),
}

export default api

