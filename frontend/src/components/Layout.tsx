import { Link, useLocation } from 'react-router-dom';
import { Map, Activity, AlertTriangle, FileText, Settings, Home } from 'lucide-react';

const Layout = ({ children }: { children: React.ReactNode }) => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-primary-800 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center space-x-2">
              <Map className="w-8 h-8" />
              <span className="text-2xl font-bold">CIVIC-EYE</span>
            </Link>
            <nav className="hidden md:flex space-x-6">
              <NavLink to="/dashboard" icon={<Home />} active={isActive('/dashboard')}>
                Dashboard
              </NavLink>
              <NavLink to="/explore" icon={<Map />} active={isActive('/explore')}>
                Explore Map
              </NavLink>
              <NavLink to="/analyze" icon={<Activity />} active={isActive('/analyze')}>
                Analyze Area
              </NavLink>
              <NavLink to="/alerts" icon={<AlertTriangle />} active={isActive('/alerts')}>
                Alerts
              </NavLink>
              <NavLink to="/reports" icon={<FileText />} active={isActive('/reports')}>
                Reports
              </NavLink>
              <NavLink to="/admin" icon={<Settings />} active={isActive('/admin')}>
                Admin
              </NavLink>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-300 py-6">
        <div className="container mx-auto px-4 text-center">
          <p>CIVIC-EYE — AI-Powered Geospatial Change Intelligence Platform</p>
          <p className="text-sm mt-2">CSE Major Project</p>
        </div>
      </footer>
    </div>
  );
};

const NavLink = ({ to, icon, active, children }: { to: string; icon: React.ReactNode; active: boolean; children: React.ReactNode }) => {
  return (
    <Link
      to={to}
      className={`flex items-center space-x-1 hover:text-primary-200 transition-colors ${
        active ? 'text-white font-semibold' : 'text-gray-300'
      }`}
    >
      {icon}
      <span>{children}</span>
    </Link>
  );
};

export default Layout;
