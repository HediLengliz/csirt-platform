import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, FileText, Activity, Plus } from 'lucide-react'
import { alertsApi, incidentsApi, eventsApi } from '../lib/api'
import StatCard from '../components/StatCard'
import AlertCard from '../components/AlertCard'
import AlertPriorityChart from '../components/Charts/AlertPriorityChart'
import AlertTrendChart from '../components/Charts/AlertTrendChart'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { data: criticalAlerts } = useQuery({
    queryKey: ['alerts', 'critical'],
    queryFn: () => alertsApi.getCritical(10).then((res) => res.data),
  })

  const { data: alerts } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertsApi.getAll({ limit: 100 }).then((res) => res.data),
  })

  const { data: incidents } = useQuery({
    queryKey: ['incidents'],
    queryFn: () => incidentsApi.getAll({ limit: 100 }).then((res) => res.data),
  })

  const { data: events } = useQuery({
    queryKey: ['events'],
    queryFn: () => eventsApi.getAll({ limit: 100 }).then((res) => res.data),
  })

  const stats = {
    criticalAlerts: alerts?.filter((a) => a.priority === 'critical').length || 0,
    totalAlerts: alerts?.filter((a) => a.status !== 'resolved').length || 0,
    activeIncidents: incidents?.filter((i) => i.status !== 'closed').length || 0,
    totalEvents: events?.length || 0,
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <p className="text-slate-400">Security incident response overview</p>
        </div>
        <div className="flex gap-2">
          <Link to="/events/new" className="btn btn-primary">
            <Plus size={18} className="mr-2" />
            Create Event
          </Link>
          <Link to="/incidents/new" className="btn btn-secondary">
            <Plus size={18} className="mr-2" />
            Create Incident
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Critical Alerts"
          value={stats.criticalAlerts}
          icon={AlertTriangle}
          color="red"
        />
        <StatCard
          title="Active Alerts"
          value={stats.totalAlerts}
          icon={AlertTriangle}
          color="yellow"
        />
        <StatCard
          title="Active Incidents"
          value={stats.activeIncidents}
          icon={FileText}
          color="purple"
        />
        <StatCard
          title="Total Events"
          value={stats.totalEvents}
          icon={Activity}
          color="blue"
        />
      </div>

      {/* Critical Alerts */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">Critical Alerts</h2>
          <Link to="/alerts" className="text-blue-400 hover:text-blue-300 text-sm">
            View all →
          </Link>
        </div>
        {criticalAlerts && criticalAlerts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {criticalAlerts.slice(0, 6).map((alert) => (
              <AlertCard key={alert.id} alert={alert} />
            ))}
          </div>
        ) : (
          <div className="card text-center py-8">
            <p className="text-slate-400">No critical alerts at this time</p>
          </div>
        )}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-bold mb-4">Recent Incidents</h2>
          <div className="card">
            {incidents && incidents.length > 0 ? (
              <div className="space-y-3">
                {incidents.slice(0, 5).map((incident) => (
                  <Link
                    key={incident.id}
                    to={`/incidents/${incident.id}`}
                    className="block p-3 rounded-lg hover:bg-slate-700 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-white">{incident.title}</p>
                        <p className="text-sm text-slate-400">{incident.status}</p>
                      </div>
                      <span className={`badge badge-${incident.severity}`}>
                        {incident.severity.toUpperCase()}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-slate-400 text-center py-4">No incidents</p>
            )}
          </div>
        </div>

        <div>
          <h2 className="text-xl font-bold mb-4">Alert Priority Distribution</h2>
          <div className="card">
            {alerts && alerts.length > 0 ? (
              <AlertPriorityChart alerts={alerts} />
            ) : (
              <p className="text-slate-400 text-center py-8">No alerts data</p>
            )}
          </div>
        </div>
      </div>

      {/* Alert Trends */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Alert Trends (Last 7 Days)</h2>
        <div className="card">
          {alerts && alerts.length > 0 ? (
            <AlertTrendChart alerts={alerts} days={7} />
          ) : (
            <p className="text-slate-400 text-center py-8">No alerts data</p>
          )}
        </div>
      </div>
    </div>
  )
}

