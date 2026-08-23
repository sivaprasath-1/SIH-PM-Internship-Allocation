import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api/client';
import {
  BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, CartesianGrid
} from 'recharts';
import { BarChart3, TrendingUp, Users, ShieldCheck, Award, MapPin } from 'lucide-react';

const COLORS = ['#1a365d', '#e67e22', '#27ae60', '#e74c3c', '#3498db', '#9c27b0', '#00bcd4', '#ff9800'];

export default function AdminAnalytics() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.getAllocationStats()
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  const locationData = stats ? Object.entries(stats.by_location || {}).map(([name, value]) => ({ name, value })) : [];
  const branchData = stats ? Object.entries(stats.by_branch || {}).map(([name, value]) => ({ name, value })) : [];
  const domainData = stats ? Object.entries(stats.by_domain || {}).map(([name, value]) => ({ name, value })) : [];
  const genderData = stats ? Object.entries(stats.by_gender || {}).map(([name, value]) => ({ name, value })) : [];

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>System Analytics & Fairness Metrics</h2>
          <p>Comprehensive monitoring of allocation efficiency, demographic balance, and skill demand</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Allocation Rate</span>
            <div className="stat-card-icon green"><TrendingUp size={20} /></div>
          </div>
          <div className="stat-card-value">{stats?.allocation_percentage || 0}%</div>
          <div className="text-sm text-muted">{stats?.allocated_students || 0} of {stats?.total_students || 0} students</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Avg Match Score</span>
            <div className="stat-card-icon blue"><Award size={20} /></div>
          </div>
          <div className="stat-card-value">{stats?.avg_match_score || 0}%</div>
          <div className="text-sm text-muted">Across all allocations</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Seat Utilization</span>
            <div className="stat-card-icon orange"><BarChart3 size={20} /></div>
          </div>
          <div className="stat-card-value">{stats?.seat_utilization || 0}%</div>
          <div className="text-sm text-muted">Of {stats?.total_seats || 0} total seats</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">First Choice Rate</span>
            <div className="stat-card-icon purple"><ShieldCheck size={20} /></div>
          </div>
          <div className="stat-card-value">{stats?.first_choice_rate || 0}%</div>
          <div className="text-sm text-muted">Received top recommendation</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Geographic Allocation Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={locationData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" fontSize={11} angle={-25} textAnchor="end" height={50} />
              <YAxis fontSize={12} />
              <Tooltip />
              <Bar dataKey="value" fill="var(--primary)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Allocation by Domain</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={domainData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={90}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {domainData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Allocation by Branch (Fairness View)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={branchData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" fontSize={12} />
              <YAxis fontSize={12} />
              <Tooltip />
              <Bar dataKey="value" fill="var(--accent)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Demographic Diversity (Gender Distribution)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={genderData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={90}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {genderData.map((_, i) => (
                  <Cell key={i} fill={COLORS[(i + 2) % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {stats?.skill_demand?.length > 0 && (
        <div className="chart-card mt-3">
          <h3>Industry Skill Demand vs Market Supply</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={stats.skill_demand} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" fontSize={12} />
              <YAxis type="category" dataKey="skill" width={140} fontSize={11} />
              <Tooltip />
              <Bar dataKey="count" fill="var(--primary)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
