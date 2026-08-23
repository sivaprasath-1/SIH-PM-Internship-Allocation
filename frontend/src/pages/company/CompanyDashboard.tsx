import React, { useEffect, useState } from 'react';
import { companyApi } from '../../api/client';
import { Briefcase, Users, ClipboardList, TrendingUp } from 'lucide-react';

export default function CompanyDashboard() {
  const [profile, setProfile] = useState<any>(null);
  const [internships, setInternships] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      companyApi.getProfile().catch(() => null),
      companyApi.getInternships().catch(() => []),
    ]).then(([p, i]) => {
      setProfile(p);
      setInternships(i || []);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  const totalSeats = internships.reduce((s: number, i: any) => s + (i.seats || 0), 0);
  const totalApps = internships.reduce((s: number, i: any) => s + (i.application_count || 0), 0);
  const filledSeats = internships.reduce((s: number, i: any) => s + (i.filled_seats || 0), 0);

  return (
    <div>
      <div className="page-header">
        <div><h2>{profile?.organization_name || 'Company Dashboard'}</h2>
          <p>Manage your internships and view applicants</p></div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-header"><span className="stat-card-label">Active Internships</span>
            <div className="stat-card-icon blue"><Briefcase size={20} /></div></div>
          <div className="stat-card-value">{internships.filter((i: any) => i.status === 'active').length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header"><span className="stat-card-label">Total Seats</span>
            <div className="stat-card-icon green"><Users size={20} /></div></div>
          <div className="stat-card-value">{totalSeats}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header"><span className="stat-card-label">Applications</span>
            <div className="stat-card-icon orange"><ClipboardList size={20} /></div></div>
          <div className="stat-card-value">{totalApps}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header"><span className="stat-card-label">Filled Seats</span>
            <div className="stat-card-icon purple"><TrendingUp size={20} /></div></div>
          <div className="stat-card-value">{filledSeats}</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><h3>Your Internships</h3></div>
        <div className="table-container">
          <table className="data-table">
            <thead><tr><th>Title</th><th>Domain</th><th>Seats</th><th>Applications</th><th>Status</th></tr></thead>
            <tbody>
              {internships.map((i: any) => (
                <tr key={i.id}>
                  <td style={{ fontWeight: 500 }}>{i.title}</td>
                  <td><span className="badge badge-blue">{i.domain}</span></td>
                  <td>{i.filled_seats || 0}/{i.seats}</td>
                  <td>{i.application_count}</td>
                  <td><span className={`badge ${i.status === 'active' ? 'badge-green' : 'badge-gray'}`}>{i.status}</span></td>
                </tr>
              ))}
              {internships.length === 0 && (
                <tr><td colSpan={5} className="text-center text-muted" style={{ padding: '2rem' }}>No internships created yet</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
