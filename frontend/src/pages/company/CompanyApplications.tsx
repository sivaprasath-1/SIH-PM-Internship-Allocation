import React, { useEffect, useState } from 'react';
import { companyApi } from '../../api/client';

export default function CompanyApplications() {
  const [internships, setInternships] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    companyApi.getInternships().then(list => {
      setInternships(list || []);
      if (list?.length > 0) {
        setSelectedId(list[0].id);
        companyApi.getApplications(list[0].id).then(setApplications).catch(() => {});
      }
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const handleSelect = async (id: number) => {
    setSelectedId(id);
    const apps = await companyApi.getApplications(id).catch(() => []);
    setApplications(apps || []);
  };

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header"><div><h2>Applications</h2><p>View applications for your internships</p></div></div>
      <div className="filter-bar">
        <select className="filter-select" value={selectedId || ''} onChange={e => handleSelect(Number(e.target.value))}>
          {internships.map(i => <option key={i.id} value={i.id}>{i.title}</option>)}
        </select>
      </div>
      <div className="card"><div className="table-container">
        <table className="data-table">
          <thead><tr><th>Student</th><th>Status</th><th>Match Score</th><th>Applied</th></tr></thead>
          <tbody>
            {applications.map((a: any) => (
              <tr key={a.id}>
                <td style={{ fontWeight: 500 }}>{a.student_name}</td>
                <td><span className={`badge ${a.status === 'pending' ? 'badge-orange' : 'badge-green'}`}>{a.status}</span></td>
                <td>{a.match_score ? `${Math.round(a.match_score)}%` : '—'}</td>
                <td className="text-muted">{a.applied_at ? new Date(a.applied_at).toLocaleDateString() : '—'}</td>
              </tr>
            ))}
            {applications.length === 0 && <tr><td colSpan={4} className="text-center text-muted" style={{ padding: '2rem' }}>No applications yet</td></tr>}
          </tbody>
        </table>
      </div></div>
    </div>
  );
}
