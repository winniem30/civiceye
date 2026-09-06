import { useState } from 'react';
import { Download, FileText, Calendar } from 'lucide-react';

const Reports = () => {
  const [selectedEvent, setSelectedEvent] = useState('');

  const handleGenerateReport = () => {
    // TODO: Implement report generation
    alert('Report generation will be implemented with backend integration');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Reports</h1>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Generate New Report */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2" />
            Generate New Report
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Change Event ID</label>
              <input
                type="text"
                className="input-field"
                placeholder="Enter event ID..."
                value={selectedEvent}
                onChange={(e) => setSelectedEvent(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Report Type</label>
              <select className="input-field">
                <option>Full Investigation Report</option>
                <option>Change Summary Report</option>
                <option>Risk Assessment Report</option>
                <option>Evidence Chain Report</option>
              </select>
            </div>
            <button
              onClick={handleGenerateReport}
              className="btn-primary w-full"
              disabled={!selectedEvent}
            >
              <Download className="w-4 h-4 mr-2 inline" />
              Generate PDF Report
            </button>
          </div>
        </div>

        {/* Recent Reports */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Calendar className="w-5 h-5 mr-2" />
            Recent Reports
          </h2>
          <div className="space-y-3">
            <ReportItem
              title="Change Event #1 - Construction Report"
              date="2024-01-15"
              type="Full Investigation"
            />
            <ReportItem
              title="Change Event #2 - Vegetation Loss Report"
              date="2024-01-14"
              type="Risk Assessment"
            />
            <ReportItem
              title="Change Event #3 - Road Expansion Report"
              date="2024-01-13"
              type="Change Summary"
            />
          </div>
        </div>

        {/* Report Template Info */}
        <div className="card lg:col-span-2">
          <h2 className="text-xl font-semibold mb-4">Report Contents</h2>
          <p className="text-gray-600 mb-4">
            Generated reports include the following information:
          </p>
          <div className="grid md:grid-cols-3 gap-4">
            <ReportSection title="Location Information" items={['Coordinates', 'Region', 'Bounds']} />
            <ReportSection title="Satellite Data" items={['Acquisition dates', 'Before/after imagery', 'Cloud cover']} />
            <ReportSection title="Change Analysis" items={['Change mask', 'Change area', 'Confidence score']} />
            <ReportSection title="Classification" items={['Human vs natural', 'Activity type', 'Classification confidence']} />
            <ReportSection title="Change DNA" items={['Growth rate', 'Persistence', 'Environmental proximity']} />
            <ReportSection title="Risk Assessment" items={['Risk score', 'Risk level', 'SHAP explanation']} />
            <ReportSection title="GIS Context" items={['Water proximity', 'Road distance', 'Protected areas']} />
            <ReportSection title="Temporal History" items={['Timeline', 'Growth pattern', 'Historical activity']} />
            <ReportSection title="Verification" items={['Verification status', 'Human review', 'Evidence']} />
          </div>
        </div>
      </div>
    </div>
  );
};

const ReportItem = ({ title, date, type }: { title: string; date: string; type: string }) => {
  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
      <h3 className="font-medium mb-1">{title}</h3>
      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>{date}</span>
        <span className="px-2 py-1 bg-gray-100 rounded text-xs">{type}</span>
      </div>
    </div>
  );
};

const ReportSection = ({ title, items }: { title: string; items: string[] }) => {
  return (
    <div>
      <h3 className="font-medium mb-2">{title}</h3>
      <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
};

export default Reports;
