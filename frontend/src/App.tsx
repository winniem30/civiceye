import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import ExploreMap from './pages/ExploreMap'
import AnalyzeArea from './pages/AnalyzeArea'
import ChangeDetails from './pages/ChangeDetails'
import Alerts from './pages/Alerts'
import Investigation from './pages/Investigation'
import Reports from './pages/Reports'
import Admin from './pages/Admin'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/explore" element={<ExploreMap />} />
          <Route path="/analyze" element={<AnalyzeArea />} />
          <Route path="/change/:id" element={<ChangeDetails />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/investigation" element={<Investigation />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
