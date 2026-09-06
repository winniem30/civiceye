import { useState } from 'react';
import { Users, Database, Settings, Activity } from 'lucide-react';

const Admin = () => {
  const [activeTab, setActiveTab] = useState<'users' | 'models' | 'system' | 'activity'>('users');

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Admin Panel</h1>

      <div className="flex space-x-8">
        {/* Sidebar */}
        <div className="w-64">
          <nav className="space-y-2">
            <TabButton
              icon={<Users className="w-4 h-4" />}
              label="Users"
              active={activeTab === 'users'}
              onClick={() => setActiveTab('users')}
            />
            <TabButton
              icon={<Database className="w-4 h-4" />}
              label="Models"
              active={activeTab === 'models'}
              onClick={() => setActiveTab('models')}
            />
            <TabButton
              icon={<Settings className="w-4 h-4" />}
              label="System"
              active={activeTab === 'system'}
              onClick={() => setActiveTab('system')}
            />
            <TabButton
              icon={<Activity className="w-4 h-4" />}
              label="Activity"
              active={activeTab === 'activity'}
              onClick={() => setActiveTab('activity')}
            />
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'users' && <UsersTab />}
          {activeTab === 'models' && <ModelsTab />}
          {activeTab === 'system' && <SystemTab />}
          {activeTab === 'activity' && <ActivityTab />}
        </div>
      </div>
    </div>
  );
};

const TabButton = ({ icon, label, active, onClick }: { icon: React.ReactNode; label: string; active: boolean; onClick: () => void }) => {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
        active ? 'bg-primary-100 text-primary-800 font-medium' : 'text-gray-600 hover:bg-gray-100'
      }`}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
};

const UsersTab = () => {
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">User Management</h2>
      <p className="text-gray-600 mb-4">Manage user accounts, roles, and permissions.</p>
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="text-left py-2">Username</th>
            <th className="text-left py-2">Email</th>
            <th className="text-left py-2">Role</th>
            <th className="text-left py-2">Status</th>
            <th className="text-left py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-b">
            <td className="py-2">admin</td>
            <td className="py-2">admin@civiceye.org</td>
            <td className="py-2"><span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">Admin</span></td>
            <td className="py-2"><span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Active</span></td>
            <td className="py-2"><button className="text-primary-600 hover:underline">Edit</button></td>
          </tr>
          <tr className="border-b">
            <td className="py-2">analyst1</td>
            <td className="py-2">analyst1@civiceye.org</td>
            <td className="py-2"><span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">Analyst</span></td>
            <td className="py-2"><span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Active</span></td>
            <td className="py-2"><button className="text-primary-600 hover:underline">Edit</button></td>
          </tr>
        </tbody>
      </table>
      <button className="btn-primary mt-4">Add New User</button>
    </div>
  );
};

const ModelsTab = () => {
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Model Management</h2>
      <p className="text-gray-600 mb-4">Manage ML models, versions, and deployment.</p>
      
      <div className="space-y-4">
        <ModelCard
          name="Change Detection (Baseline)"
          version="1.0.0"
          type="baseline"
          status="active"
          metrics={{ iou: 0.75, precision: 0.82, recall: 0.78, f1: 0.80 }}
        />
        <ModelCard
          name="Change Detection (Siamese CNN)"
          version="0.1.0"
          type="siamese_cnn"
          status="training"
          metrics={null}
        />
        <ModelCard
          name="Human Classification"
          version="1.0.0"
          type="classifier"
          status="active"
          metrics={{ accuracy: 0.85, precision: 0.87, recall: 0.83, f1: 0.85 }}
        />
      </div>
      
      <button className="btn-primary mt-4">Upload New Model</button>
    </div>
  );
};

const ModelCard = ({ name, version, type, status, metrics }: { name: string; version: string; type: string; status: string; metrics: any }) => {
  const statusColors = {
    active: 'bg-green-100 text-green-800',
    training: 'bg-yellow-100 text-yellow-800',
    inactive: 'bg-gray-100 text-gray-800',
  };

  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold">{name}</h3>
        <span className={`px-2 py-1 rounded text-xs ${statusColors[status as keyof typeof statusColors]}`}>
          {status}
        </span>
      </div>
      <div className="text-sm text-gray-600 space-y-1">
        <p>Version: {version}</p>
        <p>Type: {type}</p>
        {metrics && (
          <div className="mt-2 pt-2 border-t">
            <p className="font-medium">Metrics:</p>
            <div className="grid grid-cols-4 gap-2 text-xs">
              {Object.entries(metrics).map(([key, value]) => (
                <div key={key}>
                  <span className="text-gray-500">{key}:</span> {value as string}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const SystemTab = () => {
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">System Configuration</h2>
      <p className="text-gray-600 mb-4">Configure system settings and integrations.</p>
      
      <div className="space-y-4">
        <ConfigSection
          title="Database"
          items={[
            { label: 'Status', value: 'Connected' },
            { label: 'Type', value: 'PostgreSQL + PostGIS' },
            { label: 'Last backup', value: '2024-01-15 02:00 UTC' }
          ]}
        />
        <ConfigSection
          title="Satellite Providers"
          items={[
            { label: 'Sentinel-2', value: 'Configured (Demo Mode)' },
            { label: 'Landsat-8', value: 'Not configured' },
            { label: 'Local Dataset', value: 'Available' }
          ]}
        />
        <ConfigSection
          title="ML Services"
          items={[
            { label: 'PyTorch', value: 'Available' },
            { label: 'GPU Support', value: 'Not detected' },
            { label: 'Model Storage', value: '/data/models' }
          ]}
        />
      </div>
    </div>
  );
};

const ConfigSection = ({ title, items }: { title: string; items: { label: string; value: string }[] }) => {
  return (
    <div>
      <h3 className="font-medium mb-2">{title}</h3>
      <div className="space-y-1 text-sm">
        {items.map((item, index) => (
          <div key={index} className="flex justify-between">
            <span className="text-gray-600">{item.label}:</span>
            <span>{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const ActivityTab = () => {
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">System Activity</h2>
      <p className="text-gray-600 mb-4">Recent system activity and logs.</p>
      
      <div className="space-y-3">
        <ActivityItem
          timestamp="2024-01-15 10:30:00"
          action="Change detection completed"
          details="Event #5, method: baseline"
        />
        <ActivityItem
          timestamp="2024-01-15 10:15:00"
          action="Satellite image search"
          details="Found 3 images for selected bounds"
        />
        <ActivityItem
          timestamp="2024-01-15 09:45:00"
          action="User registered"
          details="New citizen account created"
        />
        <ActivityItem
          timestamp="2024-01-15 09:30:00"
          action="Alert generated"
          details="Critical: Unreported construction detected"
        />
      </div>
    </div>
  );
};

const ActivityItem = ({ timestamp, action, details }: { timestamp: string; action: string; details: string }) => {
  return (
    <div className="border-l-2 border-primary-200 pl-4 py-2">
      <div className="flex items-center justify-between">
        <span className="font-medium">{action}</span>
        <span className="text-sm text-gray-500">{timestamp}</span>
      </div>
      <p className="text-sm text-gray-600">{details}</p>
    </div>
  );
};

export default Admin;
