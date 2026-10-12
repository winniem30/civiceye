import { useState, useEffect } from 'react';
import { AlertTriangle, Filter, Search } from 'lucide-react';
import { alertService } from '../services/alertService';
import type { Alert } from '../types';

const Alerts = () => {
  const [filter, setFilter] = useState<'all' | 'critical' | 'high' | 'medium' | 'low'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, [filter]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const params = filter === 'all' ? {} : { severity: filter };
      const data = await alertService.listAlerts(params);
      setAlerts(data);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch = alert.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (alert.location && alert.location.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesSearch;
  });

  const severityColors = {
    critical: 'bg-red-100 text-red-800 border-red-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-green-100 text-green-800 border-green-200',
  };

  const statusColors = {
    open: 'bg-blue-100 text-blue-800',
    investigating: 'bg-purple-100 text-purple-800',
    resolved: 'bg-green-100 text-green-800',
    dismissed: 'bg-gray-100 text-gray-800',
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading alerts...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8 flex items-center">
        <AlertTriangle className="w-8 h-8 mr-3 text-red-500" />
        Alerts
      </h1>

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex items-center space-x-2 flex-1">
            <Search className="w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search alerts..."
              className="input-field"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              className="input-field"
              value={filter}
              onChange={(e) => setFilter(e.target.value as any)}
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Alert Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <AlertStatCard label="Critical" count={alerts.filter(a => a.severity === 'critical').length} color="red" />
        <AlertStatCard label="High" count={alerts.filter(a => a.severity === 'high').length} color="orange" />
        <AlertStatCard label="Medium" count={alerts.filter(a => a.severity === 'medium').length} color="yellow" />
        <AlertStatCard label="Low" count={alerts.filter(a => a.severity === 'low').length} color="green" />
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="card text-center text-gray-500">
            No alerts found matching the current filters.
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              severityColors={severityColors}
              statusColors={statusColors}
            />
          ))
        )}
      </div>
    </div>
  );
};

const AlertStatCard = ({ label, count, color }: { label: string; count: number; color: string }) => {
  const colorClasses = {
    red: 'bg-red-50 border-red-200',
    orange: 'bg-orange-50 border-orange-200',
    yellow: 'bg-yellow-50 border-yellow-200',
    green: 'bg-green-50 border-green-200',
  };

  return (
    <div className={`card ${colorClasses[color as keyof typeof colorClasses]} text-center`}>
      <p className="text-2xl font-bold">{count}</p>
      <p className="text-sm text-gray-600">{label}</p>
    </div>
  );
};

const AlertCard = ({ alert, severityColors, statusColors }: { alert: Alert; severityColors: any; statusColors: any }) => {
  return (
    <div className="card hover:shadow-lg transition-shadow cursor-pointer">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className={`px-2 py-1 rounded text-xs font-medium border ${severityColors[alert.severity as keyof typeof severityColors]}`}>
              {alert.severity.toUpperCase()}
            </span>
            {alert.alert_type === 'unreported_change' && (
              <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                Unreported
              </span>
            )}
          </div>
          <h3 className="text-lg font-semibold mb-1">{alert.title}</h3>
          <p className="text-gray-600 text-sm mb-2">{alert.description}</p>
          <p className="text-gray-500 text-sm">{alert.location}</p>
        </div>
      </div>
      <div className="flex items-center justify-between pt-3 border-t">
        <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[alert.status as keyof typeof statusColors]}`}>
          {alert.status.charAt(0).toUpperCase() + alert.status.slice(1)}
        </span>
        <span className="text-sm text-gray-500">
          {new Date(alert.created_at).toLocaleDateString()}
        </span>
      </div>
    </div>
  );
};

export default Alerts;
