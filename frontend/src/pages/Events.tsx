import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { eventsApi } from '../lib/api'
import { Activity, Search, Download, Plus } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { Link } from 'react-router-dom'
import Pagination from '../components/Pagination'
import { useToastContext } from '../hooks/useToastContext'

export default function Events() {
  const [filters, setFilters] = useState({
    source: '',
    event_type: '',
    search: '',
  })
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  const { success } = useToastContext()

  const { data: events, isLoading } = useQuery({
    queryKey: ['events', filters],
    queryFn: () => eventsApi.getAll({ ...filters, limit: 1000 }).then((res) => res.data),
  })

  const filteredEvents = events?.filter((event) => {
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      return (
        event.description?.toLowerCase().includes(searchLower) ||
        event.source_ip?.toLowerCase().includes(searchLower) ||
        event.user?.toLowerCase().includes(searchLower) ||
        event.event_type?.toLowerCase().includes(searchLower)
      )
    }
    return true
  }) || []

  const totalPages = Math.ceil(filteredEvents.length / itemsPerPage)
  const paginatedEvents = filteredEvents.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const handleExport = () => {
    const csv = [
      ['ID', 'Event Type', 'Source', 'Source IP', 'Destination IP', 'User', 'Hostname', 'Created At'],
      ...filteredEvents.map((event) => [
        event.id,
        event.event_type,
        event.source,
        event.source_ip || '',
        event.destination_ip || '',
        event.user || '',
        event.hostname || '',
        event.created_at,
      ]),
    ]
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `events-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
    success('Events exported successfully')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Events</h1>
          <p className="text-slate-400">Security event log</p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleExport} className="btn btn-secondary">
            <Download size={18} className="mr-2" />
            Export CSV
          </button>
          <Link to="/events/new" className="btn btn-primary">
            <Plus size={18} className="mr-2" />
            Create Event
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
              placeholder="Search events..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="input pl-10"
            />
          </div>

          <select
            value={filters.source}
            onChange={(e) => setFilters({ ...filters, source: e.target.value })}
            className="input"
          >
            <option value="">All Sources</option>
            <option value="splunk">Splunk</option>
            <option value="elastic">Elastic</option>
            <option value="endpoint">Endpoint</option>
            <option value="network">Network</option>
            <option value="custom">Custom</option>
          </select>

          <select
            value={filters.event_type}
            onChange={(e) => setFilters({ ...filters, event_type: e.target.value })}
            className="input"
          >
            <option value="">All Types</option>
            <option value="malware_detected">Malware Detected</option>
            <option value="suspicious_activity">Suspicious Activity</option>
            <option value="unauthorized_access">Unauthorized Access</option>
            <option value="brute_force">Brute Force</option>
            <option value="login_failure">Login Failure</option>
          </select>

          <button
            onClick={() => setFilters({ source: '', event_type: '', search: '' })}
            className="btn btn-secondary"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Events List */}
      {isLoading ? (
        <div className="card text-center py-8">
          <p className="text-slate-400">Loading events...</p>
        </div>
      ) : filteredEvents.length > 0 ? (
        <>
          <div className="space-y-4">
            {paginatedEvents.map((event) => (
              <div key={event.id} className="card">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Activity size={20} className="text-blue-400" />
                      <span className="font-semibold text-white capitalize">
                        {event.event_type.replace('_', ' ')}
                      </span>
                      <span className="badge">{event.source}</span>
                    </div>
                    {event.description && (
                      <p className="text-slate-300 mb-3">{event.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-slate-400">
                      {event.source_ip && <span>Source: {event.source_ip}</span>}
                      {event.destination_ip && <span>Dest: {event.destination_ip}</span>}
                      {event.user && <span>User: {event.user}</span>}
                      {event.hostname && <span>Host: {event.hostname}</span>}
                      <span>{formatDistanceToNow(new Date(event.created_at), { addSuffix: true })}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              totalItems={filteredEvents.length}
              itemsPerPage={itemsPerPage}
            />
          )}
        </>
      ) : (
        <div className="card text-center py-8">
          <p className="text-slate-400">No events found</p>
        </div>
      )}
    </div>
  )
}

