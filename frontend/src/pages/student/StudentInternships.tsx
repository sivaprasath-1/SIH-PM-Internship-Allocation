import React, { useEffect, useState } from 'react';
import { internshipApi } from '../../api/client';
import { MapPin, Clock, IndianRupee, Briefcase, Search, Filter } from 'lucide-react';

export default function StudentInternships() {
  const [internships, setInternships] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [domain, setDomain] = useState('');
  const [applying, setApplying] = useState<number | null>(null);
  const [msg, setMsg] = useState('');

  const loadInternships = () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (domain) params.set('domain', domain);
    internshipApi.list(params.toString())
      .then(setInternships)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadInternships(); }, [domain]);

  const handleApply = async (id: number) => {
    setApplying(id);
    try {
      await internshipApi.apply(id);
      setMsg('Application submitted successfully!');
      setTimeout(() => setMsg(''), 3000);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setApplying(null);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div><h2>Browse Internships</h2><p>Explore available internship opportunities</p></div>
      </div>

      {msg && <div className="badge badge-green" style={{ marginBottom: '1rem', padding: '0.75rem' }}>{msg}</div>}

      <div className="filter-bar">
        <input className="search-input" placeholder="Search internships..." value={search}
          onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && loadInternships()} />
        <select className="filter-select" value={domain} onChange={e => setDomain(e.target.value)}>
          <option value="">All Domains</option>
          <option value="AI/ML">AI/ML</option>
          <option value="Web Development">Web Development</option>
          <option value="Cybersecurity">Cybersecurity</option>
          <option value="Data Science">Data Science</option>
          <option value="Cloud Computing">Cloud Computing</option>
          <option value="Embedded Systems">Embedded Systems</option>
          <option value="Software Engineering">Software Engineering</option>
          <option value="IoT">IoT</option>
        </select>
        <button className="btn btn-primary btn-sm" onClick={loadInternships}><Search size={16} /> Search</button>
      </div>

      {loading ? <div className="loading-container"><div className="spinner" /></div> : (
        <div className="internship-grid">
          {internships.map((i: any) => (
            <div key={i.id} className="internship-card">
              <div className="internship-card-header">
                <div>
                  <div className="internship-card-title">{i.title}</div>
                  <div className="internship-card-company">{i.company_name}</div>
                </div>
                <span className="badge badge-blue">{i.domain}</span>
              </div>
              <div className="internship-card-meta">
                <span><MapPin size={14} /> {i.location || 'Remote'}</span>
                <span><Clock size={14} /> {i.duration}</span>
                <span><IndianRupee size={14} /> ₹{i.stipend?.toLocaleString()}/mo</span>
                <span><Briefcase size={14} /> {i.work_mode}</span>
              </div>
              <div className="internship-card-skills">
                {(i.required_skills || []).slice(0, 5).map((s: string) => (
                  <span key={s} className="skill-tag">{s}</span>
                ))}
              </div>
              <div className="internship-card-footer">
                <span className="text-sm text-muted">{i.seats - (i.filled_seats || 0)} seats left</span>
                <button className="btn btn-primary btn-sm" onClick={() => handleApply(i.id)}
                  disabled={applying === i.id}>
                  {applying === i.id ? 'Applying...' : 'Apply Now'}
                </button>
              </div>
            </div>
          ))}
          {internships.length === 0 && (
            <div className="empty-state" style={{ gridColumn: '1/-1' }}>
              <div className="empty-state-icon"><Briefcase size={28} /></div>
              <h3>No internships found</h3>
              <p>Try adjusting your search or filters</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
