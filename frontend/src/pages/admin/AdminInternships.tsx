import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api/client';

export default function AdminInternships() {
  const [data, setData] = useState<any>({ total: 0, internships: [] });
  const [loading, setLoading] = useState(true);
  const [domain, setDomain] = useState('');

  const load = () => {
    const params = new URLSearchParams();
    if (domain) params.set('domain', domain);
    adminApi.getInternships(params.toString()).then(setData).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [domain]);

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header"><div><h2>Internships</h2><p>All internship opportunities ({data.total} total)</p></div></div>
      <div className="filter-bar">
        <select className="filter-select" value={domain} onChange={e => setDomain(e.target.value)}>
          <option value="">All Domains</option>
          <option>AI/ML</option><option>Web Development</option><option>Cybersecurity</option>
          <option>Data Science</option><option>Cloud Computing</option><option>Software Engineering</option>
        </select>
      </div>
      <div className="card"><div className="table-container">
        <table className="data-table">
          <thead><tr><th>Title</th><th>Company</th><th>Domain</th><th>Location</th><th>Seats</th><th>Apps</th><th>Stipend</th><th>Status</th></tr></thead>
          <tbody>
            {data.internships.map((i: any) => (
              <tr key={i.id}>
                <td style={{ fontWeight: 500 }}>{i.title}</td>
                <td>{i.company_name}</td>
                <td><span className="badge badge-blue">{i.domain}</span></td>
                <td>{i.location}</td>
                <td>{i.filled_seats}/{i.seats}</td>
                <td>{i.application_count}</td>
                <td>₹{i.stipend?.toLocaleString()}</td>
                <td><span className={`badge ${i.status === 'active' ? 'badge-green' : 'badge-gray'}`}>{i.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div></div>
    </div>
  );
}
