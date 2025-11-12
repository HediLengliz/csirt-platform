import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Alert } from '../../lib/api'
import { format, subDays, isSameDay } from 'date-fns'

interface AlertTrendChartProps {
  alerts: Alert[]
  days?: number
}

export default function AlertTrendChart({ alerts, days = 7 }: AlertTrendChartProps) {
  const dates = Array.from({ length: days }, (_, i) => subDays(new Date(), days - 1 - i))

  const data = dates.map((date) => {
    const dayAlerts = alerts.filter((alert) =>
      isSameDay(new Date(alert.created_at), date)
    )
    return {
      date: format(date, 'MMM dd'),
      Critical: dayAlerts.filter((a) => a.priority === 'critical').length,
      High: dayAlerts.filter((a) => a.priority === 'high').length,
      Medium: dayAlerts.filter((a) => a.priority === 'medium').length,
      Low: dayAlerts.filter((a) => a.priority === 'low').length,
      Total: dayAlerts.length,
    }
  })

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="date" stroke="#9ca3af" />
        <YAxis stroke="#9ca3af" />
        <Tooltip
          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
        />
        <Legend />
        <Line type="monotone" dataKey="Critical" stroke="#ef4444" strokeWidth={2} />
        <Line type="monotone" dataKey="High" stroke="#f97316" strokeWidth={2} />
        <Line type="monotone" dataKey="Medium" stroke="#eab308" strokeWidth={2} />
        <Line type="monotone" dataKey="Low" stroke="#3b82f6" strokeWidth={2} />
        <Line type="monotone" dataKey="Total" stroke="#8b5cf6" strokeWidth={2} strokeDasharray="5 5" />
      </LineChart>
    </ResponsiveContainer>
  )
}

