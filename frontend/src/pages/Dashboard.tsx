import { useState, useEffect } from 'react';
import { AlertTriangle, Activity, Map, TrendingUp } from 'lucide-react';
import { changeDetectionService } from '../services/changeDetectionService';
import type { ChangeEvent, Alert } from '../types';

const Dashboard = () => {
  const [changeEvents, setChangeEvents] = useState<ChangeEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const events = await changeDetectionService.listChangeEvents(0, 10);
      setChangeEvents(events);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Active Alerts"
          value="3"
          icon={<AlertTriangle className="w-6 h-6 text-red-500" />}
          color="red"
        />
        <StatCard
          title="Detected Changes"
          value={changeEvents.length.toString()}
          icon={<Activity className="w-6 h-6 text-blue-500" />}
          color="blue"
        />
        <StatCard
          title="Areas Monitored"
          value="12"
          icon={<Map className="w-6 h-6 text-green-500" />}
          color="green"
        />
        <StatCard
          title="High Risk Regions"
          value="2"
          icon={<TrendingUp className="w-6 h-6 text-orange-500" />}
          color="orange"
        />
      </div>

      {/* Recent Changes */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold mb-4">Recent Change Detections</h2>
        {changeEvents.length === 0 ? (
          <p className="text-gray-500">No change events detected yet. Start by analyzing an area.</p>
        ) : (
          <div className="space-y-4">
            {changeEvents.map((event) => (
              <ChangeEventCard key={event.id} event={event} />
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        <QuickActionCard
          title="Analyze New Area"
          description="Select an area on the map and run change detection analysis."
          link="/analyze"
          linkText="Start Analysis"
        />
        <QuickActionCard
          title="View Alerts"
          description="Review active alerts and investigate potential issues."
          link="/alerts"
          linkText="View Alerts"
        />
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, color }: { title: string; value: string; icon: React.ReactNode; color: string }) => {
  const colorClasses = {
    red: 'bg-red-50 border-red-200',
    blue: 'bg-blue-50 border-blue-200',
    green: 'bg-green-50 border-green-200',
    orange: 'bg-orange-50 border-orange-200',
  };

  return (
    <div className={`card ${colorClasses[color as keyof typeof colorClasses]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm">{title}</p>
          <p className="text-3xl font-bold">{value}</p>
        </div>
        {icon}
      </div>
    </div>
  );
};

const ChangeEventCard = ({ event }: { event: ChangeEvent }) => {
  const riskLevel = event.confidence > 0.8 ? 'HIGH' : event.confidence > 0.5 ? 'MEDIUM' : 'LOW';
  const riskColors = {
    HIGH: 'bg-red-100 text-red-800',
    MEDIUM: 'bg-yellow-100 text-yellow-800',
    LOW: 'bg-green-100 text-green-800',
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold">Change Event #{event.id}</h3>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${riskColors[riskLevel as keyof typeof riskColors]}`}>
          {riskLevel}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div>
          <p className="text-gray-500">Change Area</p>
          <p className="font-medium">{event.change_area.toFixed(2)} px²</p>
        </div>
        <div>
          <p className="text-gray-500">Change %</p>
          <p className="font-medium">{event.change_percentage.toFixed(2)}%</p>
        </div>
        <div>
          <p className="text-gray-500">Confidence</p>
          <p className="font-medium">{(event.confidence * 100).toFixed(1)}%</p>
        </div>
      </div>
      {event.activity_type && (
        <div className="mt-2">
          <p className="text-gray-500 text-sm">Activity Type</p>
          <p className="font-medium capitalize">{event.activity_type}</p>
        </div>
      )}
    </div>
  );
};

const QuickActionCard = ({ title, description, link, linkText }: { title: string; description: string; link: string; linkText: string }) => {
  return (
    <div className="card hover:shadow-lg transition-shadow">
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600 mb-4">{description}</p>
      <a href={link} className="btn-primary inline-block">
        {linkText}
      </a>
    </div>
  );
};

export default Dashboard;
