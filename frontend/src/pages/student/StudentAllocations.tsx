import React, { useEffect, useState } from 'react';
import { studentApi } from '../../api/client';
import { CheckCircle, XCircle, Clock } from 'lucide-react';

export default function StudentAllocations() {
  const [allocations, setAllocations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    studentApi.getAllocations().then(setAllocations).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleAccept = async (id: number) => {
    try {
      await studentApi.acceptAllocation(id);
      load();
    } catch (err: any) { alert(err.message); }
  };

  const handleReject = async (id: number) => {
    if (!confirm('Are you sure you want to reject this allocation?')) return;
    try {
      await studentApi.rejectAllocation(id);
      load();
    } catch (err: any) { alert(err.message); }
  };

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header"><div><h2>My Allocations</h2><p>View and respond to your internship allocations</p></div></div>

      {allocations.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon"><CheckCircle size={28} /></div>
          <h3>No allocations yet</h3><p>Allocations will appear here after the admin runs the AI allocation engine</p>
        </div>
      ) : (
        <div>
          {allocations.map((a: any) => (
            <div key={a.id} className="card mb-2">
              <div className="card-body">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--primary)' }}>{a.internship_title}</h3>
                    <p className="text-sm text-muted">{a.company_name}</p>
                    <div className="mt-2">
                      <span className={`badge ${a.allocation_status === 'accepted' ? 'badge-green' : a.allocation_status === 'rejected' ? 'badge-red' : 'badge-blue'}`}>
                        {a.allocation_status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="match-score">
                    <div className={`match-score-circle ${a.match_score >= 80 ? 'match-high' : a.match_score >= 50 ? 'match-medium' : 'match-low'}`}>
                      {Math.round(a.match_score)}%
                    </div>
                  </div>
                </div>

                {a.allocation_reason && (
                  <div className="explanation-box mt-2">
                    <h4>Why you were selected:</h4>
                    <p className="text-sm">{a.allocation_reason}</p>
                  </div>
                )}

                {a.response_deadline && (
                  <p className="text-sm text-muted mt-2">
                    <Clock size={14} style={{ display: 'inline', verticalAlign: 'middle' }} /> Response deadline: {new Date(a.response_deadline).toLocaleDateString()}
                  </p>
                )}

                {a.allocation_status === 'allocated' && (
                  <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
                    <button className="btn btn-success" onClick={() => handleAccept(a.id)}>
                      <CheckCircle size={16} /> Accept Internship
                    </button>
                    <button className="btn btn-danger" onClick={() => handleReject(a.id)}>
                      <XCircle size={16} /> Reject
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
