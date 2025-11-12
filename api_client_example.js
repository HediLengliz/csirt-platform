/**
 * CSIRT Platform API Client Example
 * Ready to use in your frontend application
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

class CSIRTClient {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Helper method for API calls
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (options.body && typeof options.body === 'object') {
      config.body = JSON.stringify(options.body);
    }

    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Health Check
  async healthCheck() {
    const response = await fetch('http://localhost:8000/health');
    return response.json();
  }

  // ===== EVENTS =====
  
  async createEvent(eventData) {
    return this.request('/events/', {
      method: 'POST',
      body: eventData,
    });
  }

  async getEvents(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/events/?${queryString}`);
  }

  async getEvent(eventId) {
    return this.request(`/events/${eventId}`);
  }

  // ===== ALERTS =====
  
  async getAlerts(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/alerts/?${queryString}`);
  }

  async getCriticalAlerts(limit = 50) {
    return this.request(`/alerts/critical?limit=${limit}`);
  }

  async getAlert(alertId) {
    return this.request(`/alerts/${alertId}`);
  }

  async updateAlert(alertId, update) {
    return this.request(`/alerts/${alertId}`, {
      method: 'PATCH',
      body: update,
    });
  }

  async sendAlert(alertId) {
    return this.request(`/alerts/${alertId}/send`, {
      method: 'POST',
    });
  }

  // ===== INCIDENTS =====
  
  async createIncident(incidentData) {
    return this.request('/incidents/', {
      method: 'POST',
      body: incidentData,
    });
  }

  async getIncidents(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/incidents/?${queryString}`);
  }

  async getIncident(incidentId) {
    return this.request(`/incidents/${incidentId}`);
  }

  async updateIncident(incidentId, update) {
    return this.request(`/incidents/${incidentId}`, {
      method: 'PATCH',
      body: update,
    });
  }

  // ===== INTEGRATIONS =====
  
  async getIntegrations() {
    return this.request('/integrations/');
  }

  async createIntegration(integrationData) {
    return this.request('/integrations/', {
      method: 'POST',
      body: integrationData,
    });
  }

  async getIntegration(integrationId) {
    return this.request(`/integrations/${integrationId}`);
  }

  async testIntegration(integrationId) {
    return this.request(`/integrations/${integrationId}/test`, {
      method: 'POST',
    });
  }
}

// Usage Examples

// Initialize client
const client = new CSIRTClient();

// Example: Create an event
async function createEventExample() {
  try {
    const event = await client.createEvent({
      source: 'custom',
      event_type: 'suspicious_activity',
      raw_data: { test: 'data' },
      description: 'Suspicious activity detected',
      severity_score: '7.5',
      source_ip: '192.168.1.100',
    });
    console.log('Event created:', event);
    
    // Wait a bit for alert to be generated
    setTimeout(async () => {
      const alerts = await client.getAlerts();
      console.log('Alerts:', alerts);
    }, 2000);
  } catch (error) {
    console.error('Error creating event:', error);
  }
}

// Example: Get critical alerts
async function getCriticalAlertsExample() {
  try {
    const alerts = await client.getCriticalAlerts(10);
    console.log('Critical alerts:', alerts);
  } catch (error) {
    console.error('Error getting alerts:', error);
  }
}

// Example: Create incident from alert
async function createIncidentExample() {
  try {
    const incident = await client.createIncident({
      title: 'Security Incident',
      description: 'Incident description',
      severity: 'high',
      tags: ['malware', 'endpoint'],
      ioc: [{ type: 'ip', value: '192.168.1.100' }],
    });
    console.log('Incident created:', incident);
  } catch (error) {
    console.error('Error creating incident:', error);
  }
}

// Example: Update alert status
async function updateAlertExample(alertId) {
  try {
    const updated = await client.updateAlert(alertId, {
      status: 'resolved',
      notes: 'Resolved by analyst',
    });
    console.log('Alert updated:', updated);
  } catch (error) {
    console.error('Error updating alert:', error);
  }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CSIRTClient;
}

// Export for ES6 modules
if (typeof window !== 'undefined') {
  window.CSIRTClient = CSIRTClient;
}

