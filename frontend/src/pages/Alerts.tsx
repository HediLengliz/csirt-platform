import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertsApi } from '../lib/api'
import Pagination from '../components/Pagination'
import QuickActions from '../components/QuickActions'
import { useToastContext } from '../contexts/ToastContext'
import { Search, Download, AlertTriangle, Clock, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { Link } from 'react-router-dom'

type SortField = 'id' | 'title' | 'priority' | 'status' | 'source' | 'created_at'
type SortOrder = 'asc' | 'desc'

export default function Alerts() {
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    search: '',
  })
  const [currentPage, setCurrentPage] = useState(1)
  const [sortField, setSortField] = useState<SortField>('created_at')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const itemsPerPage = 20

  const queryClient = useQueryClient()
  const { success, error } = useToastContext()

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts', filters],
    queryFn: () => alertsApi.getAll({ ...filters, limit: 1000 }).then((res) => res.data),
  })

  const updateAlertMutation = useMutation({
    mutationFn: ({ id, update }: { id: number; update: any }) =>
      alertsApi.update(id, update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      success('Alert updated successfully')
    },
    onError: (err: any) => {
      error(err.response?.data?.detail || 'Failed to update alert')
    },
  })

  const sendAlertMutation = useMutation({
    mutationFn: (id: number) => alertsApi.send(id),
    onSuccess: () => {
      success('Alert sent to integrations')
    },
    onError: (err: any) => {
      error(err.response?.data?.detail || 'Failed to send alert')
    },
  })

  const handleUpdateStatus = (alertId: number, status: string) => {
    updateAlertMutation.mutate({ id: alertId, update: { status } })
  }

  const handleSendToIntegrations = (alertId: number) => {
    sendAlertMutation.mutate(alertId)
  }

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [filters.status, filters.priority, filters.search])

  const filteredAlerts = alerts?.filter((alert) => {
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      return (
        alert.title.toLowerCase().includes(searchLower) ||
        alert.description?.toLowerCase().includes(searchLower) ||
        alert.source.toLowerCase().includes(searchLower) ||
        alert.id.toString().includes(searchLower)
      )
    }
    return true
  }) || []

  // Sort alerts
  const sortedAlerts = [...filteredAlerts].sort((a, b) => {
    let aValue: any = a[sortField]
    let bValue: any = b[sortField]

    if (sortField === 'created_at') {
      aValue = new Date(aValue).getTime()
      bValue = new Date(bValue).getTime()
    } else if (sortField === 'priority') {
      const priorityOrder = { critical: 5, high: 4, medium: 3, low: 2, info: 1 }
      aValue = priorityOrder[aValue as keyof typeof priorityOrder] || 0
      bValue = priorityOrder[bValue as keyof typeof priorityOrder] || 0
    } else if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase()
      bValue = (bValue || '').toLowerCase()
    }

    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : aValue < bValue ? -1 : 0
    } else {
      return aValue < bValue ? 1 : aValue > bValue ? -1 : 0
    }
  })

  const totalPages = Math.ceil(sortedAlerts.length / itemsPerPage)
  const paginatedAlerts = sortedAlerts.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('asc')
    }
  }

  const handleExport = () => {
    const csv = [
      ['ID', 'Title', 'Priority', 'Status', 'Source', 'ML Score', 'Created At'],
      ...sortedAlerts.map((alert) => [
        alert.id,
        alert.title,
        alert.priority,
        alert.status,
        alert.source,
        alert.ml_score || 'N/A',
        alert.created_at,
      ]),
    ]
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `alerts-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
    success('Alerts exported successfully')
  }

  const priorityColors = {
    critical: 'badge-critical',
    high: 'badge-high',
    medium: 'badge-medium',
    low: 'badge-low',
    info: 'badge-info',
  }

  const statusColors = {
    new: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    in_progress: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    resolved: 'bg-green-500/20 text-green-400 border-green-500/30',
    false_positive: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    ignored: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  }

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <ArrowUpDown size={14} className="text-slate-400" />
    }
    return sortOrder === 'asc' ? (
      <ArrowUp size={14} className="text-blue-400" />
    ) : (
      <ArrowDown size={14} className="text-blue-400" />
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Security Alerts</h1>
          <p className="text-slate-400">Monitor and manage security alerts in real-time</p>
        </div>
        <button onClick={handleExport} className="btn btn-secondary">
          <Download size={18} className="mr-2" />
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Search alerts by ID, title, source..."
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
            <option value="new">New</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="false_positive">False Positive</option>
            <option value="ignored">Ignored</option>
          </select>

          <select
            value={filters.priority}
            onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
            className="input"
          >
            <option value="">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
            <option value="info">Info</option>
          </select>

          <button
            onClick={() => setFilters({ status: '', priority: '', search: '' })}
            className="btn btn-secondary"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-white">{sortedAlerts.length}</p>
          <p className="text-sm text-slate-400">Total Alerts</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-red-400">
            {sortedAlerts.filter((a) => a.priority === 'critical').length}
          </p>
          <p className="text-sm text-slate-400">Critical</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-orange-400">
            {sortedAlerts.filter((a) => a.priority === 'high').length}
          </p>
          <p className="text-sm text-slate-400">High</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-yellow-400">
            {sortedAlerts.filter((a) => a.status === 'new').length}
          </p>
          <p className="text-sm text-slate-400">New</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-blue-400">
            {sortedAlerts.filter((a) => a.status === 'in_progress').length}
          </p>
          <p className="text-sm text-slate-400">In Progress</p>
        </div>
      </div>

      {/* Alerts Table */}
      {isLoading ? (
        <div className="card text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading alerts...</p>
        </div>
      ) : sortedAlerts.length > 0 ? (
        <>
          <div className="card overflow-hidden p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-700/50 border-b border-slate-700">
                  <tr>
                    <th
                      className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase cursor-pointer hover:bg-slate-700 transition-colors"
                      onClick={() => handleSort('id')}
                    >
                      <div className="flex items-center gap-2">
                        ID
                        <SortIcon field="id" />
                      </div>
                    </th>
                    <th
                      className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase cursor-pointer hover:bg-slate-700 transition-colors"
                      onClick={() => handleSort('title')}
                    >
                      <div className="flex items-center gap-2">
                        Title
                        <SortIcon field="title" />
                      </div>
                    </th>
                    <th
                      className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase cursor-pointer hover:bg-slate-700 transition-colors"
                      onClick={() => handleSort('priority')}
                    >
                      <div className="flex items-center gap-2">
                        Priority
                        <SortIcon field="priority" />
                      </div>
                    </th>
                    <th
                      className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase cursor-pointer hover:bg-slate-700 transition-colors"
                      onClick={() => handleSort('status')}
                    >
                      <div className="flex items-center gap-2">
                        Status
                        <SortIcon field="status" />
                      </div>
                    </th>
                    <th
                      className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase cursor-pointer hover:bg-slate-700 transition-colors"
                      onClick={() => handleSort('source')}
                    >
                      <div className="flex items-center gap-2">
                        Source
                        <SortIcon field="source" />
                      </div>
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">
                      ML Score
                    </th>
                    <th
                      className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase cursor-pointer hover:bg-slate-700 transition-colors"
                      onClick={() => handleSort('created_at')}
                    >
                      <div className="flex items-center gap-2">
                        Created
                        <SortIcon field="created_at" />
                      </div>
                    </th>
                    <th className="px-6 py-4 text-right text-xs font-medium text-slate-300 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {paginatedAlerts.map((alert) => (
                    <tr
                      key={alert.id}
                      className="hover:bg-slate-700/30 transition-colors group"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-mono text-slate-400">#{alert.id}</span>
                      </td>
                      <td className="px-6 py-4">
                        <Link
                          to={`/alerts/${alert.id}`}
                          className="font-semibold text-white hover:text-blue-400 transition-colors block"
                        >
                          <div className="flex items-center gap-2">
                            <AlertTriangle
                              size={16}
                              className={`${
                                alert.priority === 'critical'
                                  ? 'text-red-400'
                                  : alert.priority === 'high'
                                  ? 'text-orange-400'
                                  : 'text-yellow-400'
                              }`}
                            />
                            <span className="line-clamp-1">{alert.title}</span>
                          </div>
                          {alert.description && (
                            <p className="text-xs text-slate-400 mt-1 line-clamp-1">
                              {alert.description}
                            </p>
                          )}
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`badge ${priorityColors[alert.priority]}`}>
                          {alert.priority.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`badge border ${statusColors[alert.status]}`}>
                          {alert.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-slate-300 capitalize">{alert.source}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {alert.ml_score ? (
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-2 bg-slate-700 rounded-full overflow-hidden">
                              <div
                                className={`h-full ${
                                  alert.ml_score > 0.7
                                    ? 'bg-red-500'
                                    : alert.ml_score > 0.5
                                    ? 'bg-orange-500'
                                    : 'bg-yellow-500'
                                }`}
                                style={{ width: `${alert.ml_score * 100}%` }}
                              />
                            </div>
                            <span className="text-xs text-slate-400">
                              {(alert.ml_score * 100).toFixed(0)}%
                            </span>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-500">N/A</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2 text-sm text-slate-400">
                          <Clock size={14} />
                          <span>{formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <QuickActions
                            alert={alert}
                            onUpdateStatus={(status) => handleUpdateStatus(alert.id, status)}
                            onSendToIntegrations={() => handleSendToIntegrations(alert.id)}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              totalItems={sortedAlerts.length}
              itemsPerPage={itemsPerPage}
            />
          )}
        </>
      ) : (
        <div className="card text-center py-12">
          <AlertTriangle size={48} className="mx-auto text-slate-500 mb-4" />
          <p className="text-slate-400 text-lg mb-2">No alerts found</p>
          <p className="text-slate-500 text-sm">Try adjusting your filters</p>
        </div>
      )}
    </div>
  )
}
