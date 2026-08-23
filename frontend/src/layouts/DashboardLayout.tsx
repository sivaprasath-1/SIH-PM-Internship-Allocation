import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import {
  LayoutDashboard, User, FileText, Briefcase, Star, ClipboardList,
  CheckCircle, Bell, LogOut, Menu, X, Building2, Settings, BarChart3,
  Users, BookOpen, Shield, ChevronDown
} from 'lucide-react';

const studentNav = [
  { path: '/student/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/student/profile', label: 'Profile', icon: User },
  { path: '/student/resume', label: 'Resume', icon: FileText },
  { path: '/student/internships', label: 'Internships', icon: Briefcase },
  { path: '/student/recommendations', label: 'Recommendations', icon: Star },
  { path: '/student/applications', label: 'Applications', icon: ClipboardList },
  { path: '/student/allocations', label: 'Allocations', icon: CheckCircle },
  { path: '/student/notifications', label: 'Notifications', icon: Bell },
];

const companyNav = [
  { path: '/company/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/company/profile', label: 'Profile', icon: Building2 },
  { path: '/company/internships', label: 'Internships', icon: Briefcase },
  { path: '/company/internships/create', label: 'Create Internship', icon: FileText },
  { path: '/company/applications', label: 'Applications', icon: ClipboardList },
  { path: '/company/candidates', label: 'Candidates', icon: Users },
];

const adminNav = [
  { path: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/admin/students', label: 'Students', icon: Users },
  { path: '/admin/companies', label: 'Companies', icon: Building2 },
  { path: '/admin/internships', label: 'Internships', icon: Briefcase },
  { path: '/admin/applications', label: 'Applications', icon: ClipboardList },
  { path: '/admin/allocation', label: 'Allocation', icon: Shield },
  { path: '/admin/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/admin/settings', label: 'Settings', icon: Settings },
];

export default function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const navItems = user?.role === 'admin' ? adminNav :
                   user?.role === 'company' ? companyNav : studentNav;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const roleLabel = user?.role === 'admin' ? 'Administrator' :
                    user?.role === 'company' ? 'Organization' : 'Student';

  return (
    <div className="dashboard-layout">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <Shield size={28} />
            <div>
              <h1>PM Internship</h1>
              <span>Smart Allocation Engine</span>
            </div>
          </div>
          <button className="sidebar-close" onClick={() => setSidebarOpen(false)}>
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar-link ${location.pathname === item.path ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-avatar">
              {user?.name?.charAt(0)?.toUpperCase()}
            </div>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">{user?.name}</span>
              <span className="sidebar-user-role">{roleLabel}</span>
            </div>
          </div>
          <button className="sidebar-logout" onClick={handleLogout}>
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="main-content">
        <header className="top-bar">
          <button className="menu-toggle" onClick={() => setSidebarOpen(true)}>
            <Menu size={22} />
          </button>
          <div className="top-bar-title">
            {navItems.find(i => i.path === location.pathname)?.label || 'Dashboard'}
          </div>
          <div className="top-bar-right">
            <Link to={`/${user?.role}/notifications`} className="notification-btn">
              <Bell size={20} />
            </Link>
            <div className="top-bar-user">
              <span>{user?.name}</span>
            </div>
          </div>
        </header>

        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
