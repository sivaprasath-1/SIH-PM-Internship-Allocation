import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api/client';

export default function AdminStudents() {
  const [data, setData] = useState<any>({ total: 0, students: [] });
  const [search, setSearch] = useState('');
  const [branch, setBranch] = useState('');
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  const load = () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (branch) params.set('branch', branch);
    params.set('page', page.toString());
    adminApi.getStudents(params.toString()).then(setData).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [page, branch]);

  return (
    <div>
      <div className="page-header"><div><h2>Students</h2><p>Manage registered students ({data.total} total)</p></div></div>
      <div className="filter-bar">
        <input className="search-input" placeholder="Search by name or email..." value={search}
          onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && load()} />
        <select className="filter-select" value={branch} onChange={e => { setBranch(e.target.value); setPage(1); }}>
          <option value="">All Branches</option>
          <option>CSE</option><option>IT</option><option>ECE</option><option>EEE</option><option>Mechanical</option><option>Civil</option>
        </select>
      </div>
      {loading ? <div className="loading-container"><div className="spinner" /></div> : (
        <div className="card"><div className="table-container">
          <table className="data-table">
            <thead><tr><th>Name</th><th>Email</th><th>Branch</th><th>College</th><th>CGPA</th><th>Location</th><th>Status</th></tr></thead>
            <tbody>
              {data.students.map((s: any) => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 500 }}>{s.name}</td>
                  <td className="text-muted">{s.email}</td>
                  <td><span className="badge badge-blue">{s.branch || '—'}</span></td>
                  <td>{s.college || '—'}</td>
                  <td>{s.cgpa || '—'}</td>
                  <td>{s.location || '—'}</td>
                  <td><span className={`badge ${s.is_active ? 'badge-green' : 'badge-red'}`}>{s.is_active ? 'Active' : 'Inactive'}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="card-footer flex-between">
          <span className="text-sm text-muted">Page {page} of {Math.ceil(data.total / 20)}</span>
          <div className="flex-gap">
            <button className="btn btn-outline btn-sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</button>
            <button className="btn btn-outline btn-sm" onClick={() => setPage(p => p + 1)} disabled={page * 20 >= data.total}>Next</button>
          </div>
        </div>
        </div>
      )}
    </div>
  );
}
