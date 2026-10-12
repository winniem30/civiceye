import { useState } from 'react';
import { Search, FileText, Bot } from 'lucide-react';
import { investigationService } from '../services/investigationService';
import type { Investigation } from '../types';

const Investigation = () => {
  const [selectedEventId, setSelectedEventId] = useState('');
  const [investigating, setInvestigating] = useState(false);
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [error, setError] = useState('');

  const handleInvestigate = async () => {
    if (!selectedEventId) return;

    const eventId = parseInt(selectedEventId);
    if (isNaN(eventId)) {
      setError('Please enter a valid Change Event ID');
      return;
    }

    setInvestigating(true);
    setError('');
    setInvestigation(null);

    try {
      // For MVP, we'll use a default user_id of 1
      // In production, this would come from authentication
      const newInvestigation = await investigationService.createInvestigation({
        change_event_id: eventId,
        user_id: 1 // Default user for MVP
      });
      setInvestigation(newInvestigation);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create investigation. Please check the Change Event ID.');
    } finally {
      setInvestigating(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">AI Investigation Assistant</h1>

      {/* Search */}
      <div className="card mb-6">
        <div className="flex items-center space-x-4">
          <Search className="w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Enter Change Event ID (e.g., 1, 2, 3...)"
            className="input-field flex-1"
            value={selectedEventId}
            onChange={(e) => setSelectedEventId(e.target.value)}
          />
          <button
            onClick={handleInvestigate}
            className="btn-primary"
            disabled={!selectedEventId || investigating}
          >
            {investigating ? 'Investigating...' : 'Investigate'}
          </button>
        </div>
        {error && (
          <p className="text-red-500 text-sm mt-2">{error}</p>
        )}
      </div>

      {/* Report */}
      {investigation && (
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <Bot className="w-5 h-5 text-primary-600" />
            <h2 className="text-xl font-semibold">AI Investigation Report</h2>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              investigation.status === 'completed' ? 'bg-green-100 text-green-800' :
              investigation.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {investigation.status.charAt(0).toUpperCase() + investigation.status.slice(1)}
            </span>
          </div>

          <div className="space-y-6">
            {/* AI Summary */}
            {investigation.ai_summary && (
              <div>
                <h3 className="font-medium mb-2">AI Summary</h3>
                <p className="text-gray-600">{investigation.ai_summary}</p>
              </div>
            )}

            {/* Findings */}
            {investigation.findings && (
              <div>
                <h3 className="font-medium mb-2">Key Findings</h3>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {Object.entries(investigation.findings).map(([key, value]) => (
                    <li key={key}>
                      <span className="font-medium">{key.replace(/_/g, ' ')}:</span>{' '}
                      {typeof value === 'number' ? value.toFixed(2) : String(value)}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Report */}
            {investigation.report && (
              <div>
                <h3 className="font-medium mb-2">Investigator Report</h3>
                <p className="text-gray-600">{investigation.report}</p>
              </div>
            )}

            {/* Actions */}
            <div className="flex space-x-4 pt-4 border-t">
              <button className="btn-primary">Generate PDF Report</button>
              <button className="btn-secondary">View Full Evidence</button>
              {investigation.status === 'in_progress' && (
                <button className="btn-secondary">Complete Investigation</button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      {!investigation && (
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <FileText className="w-5 h-5 text-gray-400" />
            <h2 className="text-xl font-semibold">How It Works</h2>
          </div>
          <div className="space-y-3 text-gray-600">
            <p>1. Enter a Change Event ID from the Dashboard or Alerts page</p>
            <p>2. The AI Investigation Assistant will gather all available evidence</p>
            <p>3. It will analyze satellite history, change DNA, GIS context, and risk factors</p>
            <p>4. A comprehensive investigation report will be generated</p>
            <p>5. You can then verify the change, generate reports, or take action</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Investigation;
