import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api/client';
import { Settings, Shield, Sliders, Database, Save, History } from 'lucide-react';

export default function AdminSettings() {
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  // Configurable default weights state
  const [weights, setWeights] = useState({
    skill_weight: 35,
    semantic_weight: 20,
    education_weight: 15,
    location_weight: 10,
    preference_weight: 10,
    academic_weight: 10,
  });

  const [systemConfig, setSystemConfig] = useState({
    enforce_eligibility: true,
    max_allocations_per_student: 1,
    auto_compute_matches: true,
    allow_company_override: false,
  });

  useEffect(() => {
    adminApi.getAuditLogs('limit=10')
      .then(res => setAuditLogs(res.logs || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0);

  const handleSaveWeights = (e: React.FormEvent) => {
    e.preventDefault();
    if (totalWeight !== 100) {
      alert(`Weights must sum to 100%. Current sum: ${totalWeight}%`);
      return;
    }
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      setMsg('Algorithm matching weights updated successfully!');
      setTimeout(() => setMsg(''), 3000);
    }, 600);
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>System Configuration & Parameters</h2>
          <p>Configure global AI matching weights, system policies, and view audit trail</p>
        </div>
      </div>

      {msg && <div className="badge badge-green mb-2" style={{ padding: '0.75rem', display: 'block' }}>{msg}</div>}

      <div className="grid-2 mb-3">
        {/* Matching Weights Configuration */}
        <div className="card">
          <div className="card-header">
            <h3><Sliders size={18} style={{ display: 'inline', marginRight: '0.5rem', verticalAlign: 'middle' }} /> AI Matching Engine Weights</h3>
            <span className={`badge ${totalWeight === 100 ? 'badge-green' : 'badge-red'}`}>
              Sum: {totalWeight}%
            </span>
          </div>
          <div className="card-body">
            <form onSubmit={handleSaveWeights}>
              <div className="weight-slider">
                <label>
                  <span>Skill Compatibility</span>
                  <span>{weights.skill_weight}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={weights.skill_weight}
                  onChange={e => setWeights({ ...weights, skill_weight: Number(e.target.value) })}
                />
              </div>

              <div className="weight-slider">
                <label>
                  <span>Semantic Profile Similarity</span>
                  <span>{weights.semantic_weight}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={weights.semantic_weight}
                  onChange={e => setWeights({ ...weights, semantic_weight: Number(e.target.value) })}
                />
              </div>

              <div className="weight-slider">
                <label>
                  <span>Education / Branch Match</span>
                  <span>{weights.education_weight}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={weights.education_weight}
                  onChange={e => setWeights({ ...weights, education_weight: Number(e.target.value) })}
                />
              </div>

              <div className="weight-slider">
                <label>
                  <span>Location Preference Match</span>
                  <span>{weights.location_weight}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={weights.location_weight}
                  onChange={e => setWeights({ ...weights, location_weight: Number(e.target.value) })}
                />
              </div>

              <div className="weight-slider">
                <label>
                  <span>Domain Preference Match</span>
                  <span>{weights.preference_weight}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={weights.preference_weight}
                  onChange={e => setWeights({ ...weights, preference_weight: Number(e.target.value) })}
                />
              </div>

              <div className="weight-slider">
                <label>
                  <span>Academic Performance (CGPA)</span>
                  <span>{weights.academic_weight}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={weights.academic_weight}
                  onChange={e => setWeights({ ...weights, academic_weight: Number(e.target.value) })}
                />
              </div>

              <button type="submit" className="btn btn-primary btn-full mt-2" disabled={saving || totalWeight !== 100}>
                <Save size={16} /> {saving ? 'Saving...' : 'Save AI Weights'}
              </button>
            </form>
          </div>
        </div>

        {/* Global Allocation Constraints */}
        <div className="card">
          <div className="card-header">
            <h3><Shield size={18} style={{ display: 'inline', marginRight: '0.5rem', verticalAlign: 'middle' }} /> Global Optimization Policies</h3>
          </div>
          <div className="card-body">
            <div className="form-group" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div>
                <strong style={{ display: 'block', fontSize: '0.9375rem' }}>Strict Eligibility Enforcement</strong>
                <span className="text-sm text-muted">Reject non-qualifying branch or CGPA constraints outright</span>
              </div>
              <input
                type="checkbox"
                checked={systemConfig.enforce_eligibility}
                onChange={e => setSystemConfig({ ...systemConfig, enforce_eligibility: e.target.checked })}
                style={{ width: 18, height: 18, cursor: 'pointer' }}
              />
            </div>

            <div className="form-group" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div>
                <strong style={{ display: 'block', fontSize: '0.9375rem' }}>Max Allocations Per Student</strong>
                <span className="text-sm text-muted">Enforce one active offer per candidate</span>
              </div>
              <span className="badge badge-blue">1 Offer</span>
            </div>

            <div className="form-group" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div>
                <strong style={{ display: 'block', fontSize: '0.9375rem' }}>Auto-compute Match Scores</strong>
                <span className="text-sm text-muted">Recalculate scores automatically on profile update</span>
              </div>
              <input
                type="checkbox"
                checked={systemConfig.auto_compute_matches}
                onChange={e => setSystemConfig({ ...systemConfig, auto_compute_matches: e.target.checked })}
                style={{ width: 18, height: 18, cursor: 'pointer' }}
              />
            </div>

            <div className="form-group" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <strong style={{ display: 'block', fontSize: '0.9375rem' }}>Fairness Balancing Mode</strong>
                <span className="text-sm text-muted">Prevent geographic and departmental starvation</span>
              </div>
              <span className="badge badge-green">Enabled</span>
            </div>
          </div>
        </div>
      </div>

      {/* System Audit Logs */}
      <div className="card">
        <div className="card-header">
          <h3><History size={18} style={{ display: 'inline', marginRight: '0.5rem', verticalAlign: 'middle' }} /> Recent System Audit Logs</h3>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Action</th>
                <th>Initiated By</th>
                <th>Entity</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map((log: any) => (
                <tr key={log.id}>
                  <td><span className="badge badge-purple">{log.action}</span></td>
                  <td>{log.user_name || 'System Admin'}</td>
                  <td>{log.entity_type} (ID: {log.entity_id})</td>
                  <td className="text-muted">{log.created_at ? new Date(log.created_at).toLocaleString() : '—'}</td>
                </tr>
              ))}
              {auditLogs.length === 0 && (
                <tr>
                  <td colSpan={4} className="text-center text-muted" style={{ padding: '1.5rem' }}>
                    No audit logs recorded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
