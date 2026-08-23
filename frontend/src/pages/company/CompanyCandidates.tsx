import React, { useEffect, useState } from 'react';
import { companyApi } from '../../api/client';
import { Users } from 'lucide-react';

export default function CompanyCandidates() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    companyApi.getCandidates().then(setCandidates).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header"><div><h2>Recommended Candidates</h2><p>AI-matched candidates for your internships</p></div></div>
      {candidates.length === 0 ? (
        <div className="empty-state"><div className="empty-state-icon"><Users size={28} /></div>
          <h3>No candidates yet</h3><p>Candidates will appear after the AI matching engine runs</p></div>
      ) : (
        <div className="card"><div className="table-container">
          <table className="data-table">
            <thead><tr><th>Student</th><th>Branch</th><th>CGPA</th><th>College</th><th>For Internship</th><th>Match</th></tr></thead>
            <tbody>
              {candidates.map((c: any, i: number) => (
                <tr key={i}>
                  <td style={{ fontWeight: 500 }}>{c.student_name}</td>
                  <td><span className="badge badge-blue">{c.branch}</span></td>
                  <td>{c.cgpa}</td>
                  <td>{c.college}</td>
                  <td>{c.internship_title}</td>
                  <td><span className="font-bold" style={{ color: c.match_score >= 80 ? 'var(--success)' : 'var(--warning)' }}>{Math.round(c.match_score)}%</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div></div>
      )}
    </div>
  );
}
