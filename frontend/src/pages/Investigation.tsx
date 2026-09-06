import { useState } from 'react';
import { Search, FileText, Bot } from 'lucide-react';

const Investigation = () => {
  const [selectedEventId, setSelectedEventId] = useState('');
  const [investigating, setInvestigating] = useState(false);
  const [report, setReport] = useState<any>(null);

  const handleInvestigate = async () => {
    if (!selectedEventId) return;
    
    setInvestigating(true);
    // TODO: Call investigation API
    setTimeout(() => {
      setReport({
        summary: 'AI-generated investigation summary would appear here.',
        findings: [
          'Construction activity detected in residential zone',
          'Change area: 1,250 m²',
          'Growth rate: High',
          'Risk score: 78/100 (HIGH)',
          'No matching permits found in database'
        ],
        recommendation: 'Field verification recommended'
      });
      setInvestigating(false);
    }, 2000);
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
      </div>

      {/* Report */}
      {report && (
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <Bot className="w-5 h-5 text-primary-600" />
            <h2 className="text-xl font-semibold">AI Investigation Report</h2>
          </div>
          
          <div className="space-y-6">
            {/* Summary */}
            <div>
              <h3 className="font-medium mb-2">Summary</h3>
              <p className="text-gray-600">{report.summary}</p>
            </div>

            {/* Findings */}
            <div>
              <h3 className="font-medium mb-2">Key Findings</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {report.findings.map((finding: string, index: number) => (
                  <li key={index}>{finding}</li>
                ))}
              </ul>
            </div>

            {/* Recommendation */}
            <div>
              <h3 className="font-medium mb-2">Recommendation</h3>
              <p className="text-gray-600">{report.recommendation}</p>
            </div>

            {/* Actions */}
            <div className="flex space-x-4 pt-4 border-t">
              <button className="btn-primary">Generate PDF Report</button>
              <button className="btn-secondary">View Full Evidence</button>
              <button className="btn-secondary">Verify Change</button>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      {!report && (
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
