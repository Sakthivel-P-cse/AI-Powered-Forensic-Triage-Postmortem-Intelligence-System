import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import RequireAuth from './components/RequireAuth.jsx';
import Login from './pages/Login.jsx';
import Cases from './pages/Cases.jsx';
import CaseDetail from './pages/CaseDetail.jsx';
import AutopsyView from './pages/AutopsyView.jsx';
import CCTVTimeline from './pages/CCTVTimeline.jsx';
import CorrelationMatrix from './pages/CorrelationMatrix.jsx';
import MapView from './pages/MapView.jsx';
import RiskView from './pages/RiskView.jsx';
import ReportView from './pages/ReportView.jsx';

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<RequireAuth><Layout /></RequireAuth>}>
        <Route index element={<Navigate to="/cases" replace />} />
        <Route path="/cases" element={<Cases />} />
        <Route path="/cases/:id" element={<CaseDetail />} />
        <Route path="/cases/:id/autopsy" element={<AutopsyView />} />
        <Route path="/cases/:id/cctv" element={<CCTVTimeline />} />
        <Route path="/cases/:id/correlation" element={<CorrelationMatrix />} />
        <Route path="/cases/:id/map" element={<MapView />} />
        <Route path="/cases/:id/risk" element={<RiskView />} />
        <Route path="/cases/:id/report" element={<ReportView />} />
      </Route>
      <Route path="*" element={<Navigate to="/cases" replace />} />
    </Routes>
  );
}
