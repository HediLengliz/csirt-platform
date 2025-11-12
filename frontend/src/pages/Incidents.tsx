import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { incidentsApi } from '../lib/api'
import { Link } from 'react-router-dom'
import { Search, Download, Plus } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import Pagination from '../components/Pagination'
import { useToastContext } from '../hooks/useToastContext'

export default function Incidents() {
  const [filters, setFilters] = useState({
    status: '',
    severity: '',
    search: '',
  })
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  const { success } = useToastContext()

  const { data: incidents, isLoading } = useQuery({
    queryKey: ['incidents', filters],
    queryFn: () => incidentsApi.getAll({ ...filters, limit: 1000 }).then((res) => res.data),
  })

  const filteredIncidents = incidents?.filter((incident) => {
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      return (
        incident.title.toLowerCase().includes(searchLower) ||
        incident.description?.toLowerCase().includes(searchLower) ||
        incident.assigned_to?.toLowerCase().includes(searchLower)
      )
    }
    return true
  }) || []

  const totalPages = Math.ceil(filteredIncidents.length / itemsPerPage)
  const paginatedIncidents = filteredIncidents.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const handleExport = () => {
    const csv = [
      ['ID', 'Title', 'Severity', 'Status', 'Assigned To', 'Created At'],
      ...filteredIncidents.map((incident) => [
        incident.id,
        incident.title,
        incident.severity,
        incident.status,
        incident.assigned_to || 'Unassigned',
        incident.created_at,
      ]),
    ]
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `incidents-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
    success('Incidents exported successfully')
  }

  const severityColors = {
    critical: 'badge-critical',
    high: 'badge-high',
    medium: 'badge-medium',
    low: 'badge-low',
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Incidents</h1>
          <p className="text-slate-400">Manage security incidents</p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleExport} className="btn btn-secondary">
            <Download size={18} className="mr-2" />
            Export CSV
          </button>
          <Link to="/incidents/new" className="btn btn-primary">
            <Plus size={18} className="mr-2" />
            Create Incident
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Search incidents..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="input pl-10"
            />
          </div>

          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="input"
          >
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="contained">Contained</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>

          <select
            value={filters.severity}
            onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
            className="input"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <button
            onClick={() => setFilters({ status: '', severity: '', search: '' })}
            className="btn btn-secondary"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Incidents Table */}
      {isLoading ? (
        <div className="card text-center py-8">
          <p className="text-slate-400">Loading incidents...</p>
        </div>
      ) : filteredIncidents.length > 0 ? (
        <>
          <div className="card overflow-hidden p-0">
            <table className="w-full">
              <thead className="bg-slate-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Title</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Severity</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Assigned To</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {paginatedIncidents.map((incident) => (
                  <tr
                    key={incident.id}
                    className="hover:bg-slate-700 transition-colors cursor-pointer"
                  >
                    <td className="px-6 py-4">
                      <Link
                        to={`/incidents/${incident.id}`}
                        className="font-semibold text-white hover:text-blue-400"
                      >
                        {incident.title}
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`badge ${severityColors[incident.severity]}`}>
                        {incident.severity.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="badge">{incident.status}</span>
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {incident.assigned_to || 'Unassigned'}
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {formatDistanceToNow(new Date(incident.created_at), { addSuffix: true })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              totalItems={filteredIncidents.length}
              itemsPerPage={itemsPerPage}
            />
          )}
        </>
      ) : (
        <div className="card text-center py-8">
          <p className="text-slate-400">No incidents found</p>
        </div>
      )}
    </div>
  )
}

