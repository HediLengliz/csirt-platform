import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import Incidents from './pages/Incidents'
import Events from './pages/Events'
import AlertDetail from './pages/AlertDetail'
import IncidentDetail from './pages/IncidentDetail'
import CreateEvent from './pages/CreateEvent'
import CreateIncident from './pages/CreateIncident'
import MLStats from './pages/MLStats'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/alerts/:id" element={<AlertDetail />} />
        <Route path="/incidents" element={<Incidents />} />
        <Route path="/incidents/new" element={<CreateIncident />} />
        <Route path="/incidents/:id" element={<IncidentDetail />} />
        <Route path="/events" element={<Events />} />
        <Route path="/events/new" element={<CreateEvent />} />
        <Route path="/ml" element={<MLStats />} />
      </Routes>
    </Layout>
  )
}

export default App

