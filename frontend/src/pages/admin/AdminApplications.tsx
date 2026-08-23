import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api/client';

export default function AdminApplications() {
  const [data, setData] = useState<any>({ total: 0, applications: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.getApplications().then(setData).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header"><div><h2>Applications</h2><p>All student applications ({data.total} total)</p></div></div>
      <div className="card"><div className="table-container">
        <table className="data-table">
          <thead><tr><th>Student</th><th>Internship</th><th>Company</th><th>Status</th><th>Applied</th></tr></thead>
          <tbody>
            {data.applications.map((a: any) => (
              <tr key={a.id}>
                <td style={{ fontWeight: 500 }}>{a.student_name}</td>
                <td>{a.internship_title}</td>
                <td>{a.company_name}</td>
                <td><span className={`badge ${a.status === 'pending' ? 'badge-orange' : a.status === 'allocated' ? 'badge-green' : 'badge-gray'}`}>{a.status}</span></td>
                <td className="text-muted">{a.applied_at ? new Date(a.applied_at).toLocaleDateString() : ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div></div>
    </div>
  );
}
