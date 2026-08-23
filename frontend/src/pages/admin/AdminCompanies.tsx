import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api/client';
import { CheckCircle, XCircle } from 'lucide-react';

export default function AdminCompanies() {
  const [data, setData] = useState<any>({ total: 0, companies: [] });
  const [loading, setLoading] = useState(true);

  const load = () => { adminApi.getCompanies().then(setData).catch(() => {}).finally(() => setLoading(false)); };
  useEffect(() => { load(); }, []);

  const verify = async (id: number, action: string) => {
    try { await adminApi.verifyCompany(id, action); load(); }
    catch (err: any) { alert(err.message); }
  };

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header"><div><h2>Companies</h2><p>Manage registered organizations ({data.total} total)</p></div></div>
      <div className="card"><div className="table-container">
        <table className="data-table">
          <thead><tr><th>Organization</th><th>Industry</th><th>Location</th><th>Internships</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            {data.companies.map((c: any) => (
              <tr key={c.id}>
                <td style={{ fontWeight: 500 }}>{c.organization_name}</td>
                <td>{c.industry || '—'}</td>
                <td>{c.location || '—'}</td>
                <td>{c.internship_count}</td>
                <td><span className={`badge ${c.verification_status === 'verified' ? 'badge-green' : c.verification_status === 'pending' ? 'badge-orange' : 'badge-red'}`}>{c.verification_status}</span></td>
                <td>
                  {c.verification_status !== 'verified' && (
                    <button className="btn btn-success btn-sm" onClick={() => verify(c.id, 'verified')}><CheckCircle size={14} /> Verify</button>
                  )}
                  {c.verification_status === 'verified' && (
                    <button className="btn btn-ghost btn-sm" onClick={() => verify(c.id, 'rejected')}><XCircle size={14} /></button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div></div>
    </div>
  );
}
