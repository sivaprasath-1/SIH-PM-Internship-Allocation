import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { companyApi } from '../../api/client';
import { Plus, Trash2, Edit, Briefcase } from 'lucide-react';

export default function CompanyInternships() {
  const [internships, setInternships] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => { companyApi.getInternships().then(setInternships).catch(() => {}).finally(() => setLoading(false)); };
  useEffect(() => { load(); }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this internship?')) return;
    try { await companyApi.deleteInternship(id); load(); }
    catch (err: any) { alert(err.message); }
  };

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div><h2>Manage Internships</h2></div>
        <Link to="/company/internships/create" className="btn btn-primary"><Plus size={16} /> Create Internship</Link>
      </div>

      {internships.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon"><Briefcase size={28} /></div>
          <h3>No internships yet</h3><p>Create your first internship opportunity</p>
        </div>
      ) : (
        <div className="card"><div className="table-container">
          <table className="data-table">
            <thead><tr><th>Title</th><th>Domain</th><th>Location</th><th>Seats</th><th>Applications</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              {internships.map((i: any) => (
                <tr key={i.id}>
                  <td style={{ fontWeight: 500 }}>{i.title}</td>
                  <td><span className="badge badge-blue">{i.domain}</span></td>
                  <td>{i.location}</td>
                  <td>{i.filled_seats || 0}/{i.seats}</td>
                  <td>{i.application_count}</td>
                  <td><span className={`badge ${i.status === 'active' ? 'badge-green' : 'badge-gray'}`}>{i.status}</span></td>
                  <td>
                    <button className="btn btn-ghost btn-sm" onClick={() => handleDelete(i.id)}><Trash2 size={14} /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div></div>
      )}
    </div>
  );
}
