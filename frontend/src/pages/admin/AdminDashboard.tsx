import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api/client';
import { BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { Users, Building2, Briefcase, CheckCircle, TrendingUp, AlertTriangle, BarChart3, Percent } from 'lucide-react';

const COLORS = ['#1a365d', '#e67e22', '#27ae60', '#e74c3c', '#3498db', '#9c27b0', '#00bcd4', '#ff9800'];

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.getDashboard().then(setStats).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;
  if (!stats) return <div className="error-msg">Failed to load dashboard</div>;

  const branchData = Object.entries(stats.students_by_branch || {}).map(([name, value]) => ({ name, value }));
  const domainData = Object.entries(stats.internships_by_domain || {}).map(([name, value]) => ({ name, value }));

  return (
    <div>
      <div className="page-header">
        <div><h2>Admin Dashboard</h2><p>PM Internship Smart Allocation Engine — System Overview</p></div>
      </div>

      <div className="stats-grid">
        <div className="stat-card"><div className="stat-card-header"><span className="stat-card-label">Total Students</span>
          <div className="stat-card-icon blue"><Users size={20} /></div></div>
          <div className="stat-card-value">{stats.total_students}</div></div>
        <div className="stat-card"><div className="stat-card-header"><span className="stat-card-label">Total Companies</span>
          <div className="stat-card-icon green"><Building2 size={20} /></div></div>
          <div className="stat-card-value">{stats.total_companies}</div>
          <div className="text-sm text-muted">{stats.verified_companies} verified</div></div>
        <div className="stat-card"><div className="stat-card-header"><span className="stat-card-label">Active Internships</span>
          <div className="stat-card-icon orange"><Briefcase size={20} /></div></div>
          <div className="stat-card-value">{stats.active_internships}</div>
          <div className="text-sm text-muted">{stats.total_seats} total seats</div></div>
        <div className="stat-card"><div className="stat-card-header"><span className="stat-card-label">Applications</span>
          <div className="stat-card-icon purple"><TrendingUp size={20} /></div></div>
          <div className="stat-card-value">{stats.total_applications}</div></div>
        <div className="stat-card"><div className="stat-card-header"><span className="stat-card-label">Allocated Students</span>
          <div className="stat-card-icon green"><CheckCircle size={20} /></div></div>
          <div className="stat-card-value">{stats.allocated_students}</div>
          <div className="text-sm text-muted">{stats.allocation_percentage}% allocation rate</div></div>
        <div className="stat-card"><div className="stat-card-header"><span className="stat-card-label">Unallocated</span>
          <div className="stat-card-icon red"><AlertTriangle size={20} /></div></div>
          <div className="stat-card-value">{stats.unallocated_students}</div></div>
        <div className="stat-card"><div className="stat-card-header"><span className="stat-card-label">Avg Match Score</span>
          <div className="stat-card-icon blue"><BarChart3 size={20} /></div></div>
          <div className="stat-card-value">{stats.avg_match_score}%</div></div>
        <div className="stat-card"><div className="stat-card-header"><span className="stat-card-label">Allocation %</span>
          <div className="stat-card-icon orange"><Percent size={20} /></div></div>
          <div className="stat-card-value">{stats.allocation_percentage}%</div></div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Students by Branch</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={branchData}>
              <XAxis dataKey="name" fontSize={12} />
              <YAxis fontSize={12} />
              <Tooltip />
              <Bar dataKey="value" fill="var(--primary)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-card">
          <h3>Internships by Domain</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={domainData} dataKey="value" nameKey="name" cx="50%" cy="50%"
                outerRadius={100} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {domainData.map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><h3>Recent Applications</h3></div>
        <div className="table-container">
          <table className="data-table">
            <thead><tr><th>Student</th><th>Internship</th><th>Company</th><th>Status</th><th>Date</th></tr></thead>
            <tbody>
              {(stats.recent_applications || []).map((a: any) => (
                <tr key={a.id}>
                  <td style={{ fontWeight: 500 }}>{a.student_name}</td>
                  <td>{a.internship_title}</td>
                  <td>{a.company_name}</td>
                  <td><span className={`badge ${a.status === 'pending' ? 'badge-orange' : 'badge-green'}`}>{a.status}</span></td>
                  <td className="text-muted">{a.applied_at ? new Date(a.applied_at).toLocaleDateString() : ''}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
