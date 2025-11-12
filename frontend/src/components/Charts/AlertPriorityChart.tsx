import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { Alert } from '../../lib/api'

interface AlertPriorityChartProps {
  alerts: Alert[]
}

const COLORS = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#3b82f6',
  info: '#6b7280',
}

export default function AlertPriorityChart({ alerts }: AlertPriorityChartProps) {
  const data = [
    { name: 'Critical', value: alerts.filter((a) => a.priority === 'critical').length, color: COLORS.critical },
    { name: 'High', value: alerts.filter((a) => a.priority === 'high').length, color: COLORS.high },
    { name: 'Medium', value: alerts.filter((a) => a.priority === 'medium').length, color: COLORS.medium },
    { name: 'Low', value: alerts.filter((a) => a.priority === 'low').length, color: COLORS.low },
    { name: 'Info', value: alerts.filter((a) => a.priority === 'info').length, color: COLORS.info },
  ].filter((item) => item.value > 0)

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}

