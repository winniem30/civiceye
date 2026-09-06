import { Link } from 'react-router-dom';
import { Map, Activity, AlertTriangle, Shield, TrendingUp, Eye } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-800 to-primary-900 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <div className="flex justify-center mb-6">
            <Map className="w-20 h-20" />
          </div>
          <h1 className="text-5xl font-bold mb-4">CIVIC-EYE</h1>
          <p className="text-2xl mb-2">AI-Powered Geospatial Change Intelligence Platform</p>
          <p className="text-lg text-primary-200 mb-8 max-w-3xl mx-auto">
            Transforming satellite imagery from passive observation into proactive detection, 
            contextual risk assessment and early warning of human-induced environmental and infrastructure changes.
          </p>
          <div className="flex justify-center space-x-4">
            <Link to="/explore" className="btn-primary text-lg px-8 py-3">
              Explore Map
            </Link>
            <Link to="/analyze" className="bg-white text-primary-800 px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors text-lg">
              Analyze Area
            </Link>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">The Challenge</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card text-center">
              <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Unreported Changes</h3>
              <p className="text-gray-600">
                Many environmental and infrastructure changes go unreported until they become critical problems.
              </p>
            </div>
            <div className="card text-center">
              <Activity className="w-12 h-12 text-orange-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Delayed Response</h3>
              <p className="text-gray-600">
                Manual monitoring is slow and resource-intensive, leading to delayed responses to emerging threats.
              </p>
            </div>
            <div className="card text-center">
              <Shield className="w-12 h-12 text-blue-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Limited Context</h3>
              <p className="text-gray-600">
                Existing tools detect changes but lack the intelligence to understand context, risk, and implications.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">The CIVIC-EYE Solution</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FeatureCard
              icon={<Eye className="w-8 h-8" />}
              title="Detect"
              description="Multi-temporal satellite imagery analysis to identify changes over time."
            />
            <FeatureCard
              icon={<Activity className="w-8 h-8" />}
              title="Classify"
              description="AI-powered classification of human vs natural changes and activity types."
            />
            <FeatureCard
              icon={<TrendingUp className="w-8 h-8" />}
              title="Track"
              description="Temporal tracking of change patterns, growth rates, and historical activity."
            />
            <FeatureCard
              icon={<Shield className="w-8 h-8" />}
              title="Assess"
              description="Risk assessment with GIS context analysis and explainable AI insights."
            />
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="max-w-4xl mx-auto">
            <WorkflowStep
              step={1}
              title="Select Area of Interest"
              description="Use the interactive map to select a region and choose dates for comparison."
            />
            <WorkflowStep
              step={2}
              title="Retrieve Satellite Imagery"
              description="Automatically fetch satellite imagery from Sentinel-2 or other providers."
            />
            <WorkflowStep
              step={3}
              title="AI Analysis"
              description="Run change detection, classify human activity, and assess risk automatically."
            />
            <WorkflowStep
              step={4}
              title="Investigate & Act"
              description="Review evidence, verify findings, and generate reports for action."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-primary-800 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-xl mb-8 text-primary-200">
            Begin monitoring environmental and infrastructure changes today.
          </p>
          <Link to="/explore" className="bg-white text-primary-800 px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors text-lg">
            Launch Platform
          </Link>
        </div>
      </section>
    </div>
  );
};

const FeatureCard = ({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) => {
  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="text-primary-600 mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
};

const WorkflowStep = ({ step, title, description }: { step: number; title: string; description: string }) => {
  return (
    <div className="flex items-start space-x-4 mb-8">
      <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold">
        {step}
      </div>
      <div className="flex-1">
        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
      </div>
    </div>
  );
};

export default LandingPage;
