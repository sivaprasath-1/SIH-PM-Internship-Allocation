import React, { useEffect, useState } from 'react';
import { studentApi } from '../../api/client';
import { ClipboardList } from 'lucide-react';

export default function StudentApplications() {
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    studentApi.getApplications().then(setApplications).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  const statusBadge = (status: string) => {
    const map: Record<string, string> = {
      pending: 'badge-orange', reviewed: 'badge-blue', shortlisted: 'badge-green',
      rejected: 'badge-red', allocated: 'badge-purple', withdrawn: 'badge-gray',
    };
    return map[status] || 'badge-gray';
  };

  return (
    <div>
      <div className="page-header"><div><h2>My Applications</h2><p>Track your internship applications</p></div></div>

      {applications.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon"><ClipboardList size={28} /></div>
          <h3>No applications yet</h3><p>Browse internships and start applying</p>
        </div>
      ) : (
        <div className="card">
          <div className="table-container">
            <table className="data-table">
              <thead><tr><th>Internship</th><th>Company</th><th>Status</th><th>Match Score</th><th>Applied On</th></tr></thead>
              <tbody>
                {applications.map((a: any) => (
                  <tr key={a.id}>
                    <td style={{ fontWeight: 500 }}>{a.internship_title}</td>
                    <td>{a.company_name}</td>
                    <td><span className={`badge ${statusBadge(a.status)}`}>{a.status}</span></td>
                    <td>{a.match_score ? `${Math.round(a.match_score)}%` : '—'}</td>
                    <td className="text-muted">{a.applied_at ? new Date(a.applied_at).toLocaleDateString() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
