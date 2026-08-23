import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './hooks/useAuth';
import DashboardLayout from './layouts/DashboardLayout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import StudentDashboard from './pages/student/StudentDashboard';
import StudentProfile from './pages/student/StudentProfile';
import StudentResume from './pages/student/StudentResume';
import StudentInternships from './pages/student/StudentInternships';
import StudentRecommendations from './pages/student/StudentRecommendations';
import StudentApplications from './pages/student/StudentApplications';
import StudentAllocations from './pages/student/StudentAllocations';
import StudentNotifications from './pages/student/StudentNotifications';
import CompanyDashboard from './pages/company/CompanyDashboard';
import CompanyProfile from './pages/company/CompanyProfile';
import CompanyInternships from './pages/company/CompanyInternships';
import CreateInternship from './pages/company/CreateInternship';
import CompanyApplications from './pages/company/CompanyApplications';
import CompanyCandidates from './pages/company/CompanyCandidates';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminStudents from './pages/admin/AdminStudents';
import AdminCompanies from './pages/admin/AdminCompanies';
import AdminInternships from './pages/admin/AdminInternships';
import AdminApplications from './pages/admin/AdminApplications';
import AdminAllocation from './pages/admin/AdminAllocation';
import AdminAnalytics from './pages/admin/AdminAnalytics';
import AdminSettings from './pages/admin/AdminSettings';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
});

function ProtectedRoute({ children, role }: { children: React.ReactNode; role?: string }) {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return <div className="loading-container"><div className="spinner" /></div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (role && user?.role !== role) {
    return <Navigate to={`/${user?.role}/dashboard`} replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return <div className="loading-container"><div className="spinner" /></div>;
  }

  return (
    <Routes>
      {/* Auth routes */}
      <Route path="/login" element={
        isAuthenticated ? <Navigate to={`/${user?.role}/dashboard`} /> : <LoginPage />
      } />
      <Route path="/register" element={
        isAuthenticated ? <Navigate to={`/${user?.role}/dashboard`} /> : <RegisterPage />
      } />

      {/* Student routes */}
      <Route path="/student" element={
        <ProtectedRoute role="student"><DashboardLayout /></ProtectedRoute>
      }>
        <Route path="dashboard" element={<StudentDashboard />} />
        <Route path="profile" element={<StudentProfile />} />
        <Route path="resume" element={<StudentResume />} />
        <Route path="internships" element={<StudentInternships />} />
        <Route path="recommendations" element={<StudentRecommendations />} />
        <Route path="applications" element={<StudentApplications />} />
        <Route path="allocations" element={<StudentAllocations />} />
        <Route path="notifications" element={<StudentNotifications />} />
      </Route>

      {/* Company routes */}
      <Route path="/company" element={
        <ProtectedRoute role="company"><DashboardLayout /></ProtectedRoute>
      }>
        <Route path="dashboard" element={<CompanyDashboard />} />
        <Route path="profile" element={<CompanyProfile />} />
        <Route path="internships" element={<CompanyInternships />} />
        <Route path="internships/create" element={<CreateInternship />} />
        <Route path="applications" element={<CompanyApplications />} />
        <Route path="candidates" element={<CompanyCandidates />} />
      </Route>

      {/* Admin routes */}
      <Route path="/admin" element={
        <ProtectedRoute role="admin"><DashboardLayout /></ProtectedRoute>
      }>
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="students" element={<AdminStudents />} />
        <Route path="companies" element={<AdminCompanies />} />
        <Route path="internships" element={<AdminInternships />} />
        <Route path="applications" element={<AdminApplications />} />
        <Route path="allocation" element={<AdminAllocation />} />
        <Route path="analytics" element={<AdminAnalytics />} />
        <Route path="settings" element={<AdminSettings />} />
      </Route>

      {/* Default redirect */}
      <Route path="/" element={
        isAuthenticated ? <Navigate to={`/${user?.role}/dashboard`} /> : <Navigate to="/login" />
      } />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
