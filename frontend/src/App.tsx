import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import JDAudit from './pages/JDAudit';
import ResumeShield from './pages/ResumeShield';
import InterviewMonitor from './pages/InterviewMonitor';
import ComplianceReport from './pages/ComplianceReport';
import { useAuthStore } from './stores/authStore';
import { canAccessRoute, getRoleHome } from './authz';

const PrivateRoute: React.FC<{ children: React.ReactNode; path?: string }> = ({ children, path }) => {
  const { isAuthenticated, user } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" />;
  if (path && !canAccessRoute(user?.role, path)) {
    return <Navigate to={getRoleHome(user?.role)} replace />;
  }
  return <>{children}</>;
};

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }>
            <Route index element={
              <PrivateRoute path="/">
                <Dashboard />
              </PrivateRoute>
            } />
            <Route path="jd-audit" element={
              <PrivateRoute path="/jd-audit">
                <JDAudit />
              </PrivateRoute>
            } />
            <Route path="resume-shield" element={
              <PrivateRoute path="/resume-shield">
                <ResumeShield />
              </PrivateRoute>
            } />
            <Route path="interview-monitor" element={
              <PrivateRoute path="/interview-monitor">
                <InterviewMonitor />
              </PrivateRoute>
            } />
            <Route path="compliance-report" element={
              <PrivateRoute path="/compliance-report">
                <ComplianceReport />
              </PrivateRoute>
            } />
          </Route>
        </Routes>
      </Router>
    </ConfigProvider>
  );
}

export default App;
