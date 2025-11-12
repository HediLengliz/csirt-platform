# CSIRT Platform Frontend

Modern React + TypeScript frontend for the CSIRT Platform.

## Features

- 🎨 **Modern UI**: Dark theme optimized for security operations
- 📊 **Dashboard**: Real-time overview of alerts, incidents, and events
- 🔔 **Alerts Management**: View, filter, and manage security alerts
- 📋 **Incidents Management**: Track and manage security incidents
- 📈 **Event Log**: View security events with filtering
- ⚡ **Real-time Updates**: Automatic data refresh every 5 seconds
- 🎯 **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Query** - Data fetching and caching
- **React Router** - Navigation
- **Axios** - HTTP client
- **Lucide React** - Icons
- **Date-fns** - Date formatting

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Build

```bash
npm run build
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Architecture

### Components
- `Layout` - Main layout with sidebar navigation
- `StatCard` - Dashboard statistics card
- `AlertCard` - Alert display card

### Pages
- `Dashboard` - Main dashboard with overview
- `Alerts` - Alerts list and management
- `AlertDetail` - Alert details view
- `Incidents` - Incidents list
- `IncidentDetail` - Incident details view
- `Events` - Events log

### API Client
- `lib/api.ts` - API client with all endpoints

## Features

### Dashboard
- Critical alerts counter
- Active alerts and incidents
- Recent alerts display
- Alert priority distribution
- Recent incidents list

### Alerts
- List all alerts
- Filter by status and priority
- Search functionality
- Alert details view
- Update alert status
- Send alerts to integrations

### Incidents
- List all incidents
- Filter by status and severity
- Search functionality
- Incident details view
- Create new incidents

### Events
- View security events
- Filter by source and type
- Search functionality
- Event details

## Integration with Backend

The frontend connects to the backend API at `http://localhost:8000/api/v1` by default. Make sure the backend is running before starting the frontend.

## Real-time Updates

The frontend automatically refreshes data every 5 seconds using React Query's refetch interval. This ensures you always see the latest alerts and incidents.

## Responsive Design

The frontend is fully responsive and works on:
- Desktop (1920px+)
- Laptop (1024px+)
- Tablet (768px+)
- Mobile (320px+)
