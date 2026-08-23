import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api/client';
import { BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';
import { Play, RefreshCw, Download, Users, AlertTriangle, CheckCircle, TrendingUp, Zap } from 'lucide-react';

const COLORS = ['#1a365d', '#e67e22', '#27ae60', '#e74c3c', '#3498db', '#9c27b0', '#00bcd4', '#ff9800'];

export default function AdminAllocation() {
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [unallocated, setUnallocated] = useState<any[]>([]);
  const [unfilled, setUnfilled] = useState<any[]>([]);
  const [runResult, setRunResult] = useState<any>(null);
  const [tab, setTab] = useState('overview');

  const [config, setConfig] = useState({
    skill_weight: 0.35, semantic_weight: 0.20, education_weight: 0.15,
    location_weight: 0.10, preference_weight: 0.10, academic_weight: 0.10,
    enforce_eligibility: true, max_allocations_per_student: 1,
  });

  const loadData = async () => {
    try {
      const [r, s, u, uf] = await Promise.all([
        adminApi.getAllocationResults().catch(() => []),
        adminApi.getAllocationStats().catch(() => null),
        adminApi.getUnallocatedStudents().catch(() => []),
        adminApi.getUnfilledInternships().catch(() => []),
      ]);
      setResults(r || []);
      setStats(s);
      setUnallocated(u || []);
      setUnfilled(uf || []);
    } catch {}
  };

  useEffect(() => { loadData(); }, []);

  const handleRun = async () => {
    setRunning(true);
    setRunResult(null);
    try {
      const result = await adminApi.runAllocation(config);
      setRunResult(result);
      await loadData();
    } catch (err: any) {
      alert('Allocation failed: ' + err.message);
    } finally {
      setRunning(false);
    }
  };

  const locationData = stats ? Object.entries(stats.by_location || {}).map(([name, value]) => ({ name, value })) : [];
  const branchData = stats ? Object.entries(stats.by_branch || {}).map(([name, value]) => ({ name, value })) : [];
  const domainData = stats ? Object.entries(stats.by_domain || {}).map(([name, value]) => ({ name, value })) : [];

  return (
    <div>
      <div className="page-header">
        <div><h2>AI Allocation Engine</h2><p>Run smart allocation and view results</p></div>
        <div className="flex-gap">
          <button className="btn btn-primary btn-lg" onClick={handleRun} disabled={running}>
            {running ? <><RefreshCw size={16} className="spin" /> Running...</> : <><Zap size={16} /> Run AI Allocation</>}
          </button>
        </div>
      </div>

      {/* Allocation Configuration */}
      <div className="allocation-panel mb-3">
        <h2>⚙️ Allocation Configuration</h2>
        <div className="grid-3">
          {[
            { key: 'skill_weight', label: 'Skill Weight' },
            { key: 'semantic_weight', label: 'Semantic Weight' },
            { key: 'education_weight', label: 'Education Weight' },
            { key: 'location_weight', label: 'Location Weight' },
            { key: 'preference_weight', label: 'Preference Weight' },
            { key: 'academic_weight', label: 'Academic Weight' },
          ].map(({ key, label }) => (
            <div key={key} className="weight-slider">
              <label>
                <span>{label}</span>
                <span>{((config as any)[key] * 100).toFixed(0)}%</span>
              </label>
              <input type="range" min="0" max="100" value={(config as any)[key] * 100}
                onChange={e => setConfig({ ...config, [key]: parseInt(e.target.value) / 100 })} />
            </div>
          ))}
        </div>
      </div>

      {/* Running state */}
      {running && (
        <div className="allocation-progress">
          <div className="spinner" style={{ width: 60, height: 60, borderWidth: 4, margin: '0 auto 1rem' }} />
          <h3>Running AI Allocation Engine...</h3>
          <p className="text-muted">Computing match scores, applying constraints, and optimizing allocations</p>
        </div>
      )}

      {/* Run result */}
      {runResult && (
        <div className="allocation-results mb-3">
          <h3 style={{ color: 'var(--success)', marginBottom: '1rem' }}>✅ Allocation Complete!</h3>
          <div className="stats-grid">
            <div className="stat-card"><div className="stat-card-label">Total Students</div><div className="stat-card-value">{runResult.total_students}</div></div>
            <div className="stat-card"><div className="stat-card-label">Total Internships</div><div className="stat-card-value">{runResult.total_internships}</div></div>
            <div className="stat-card"><div className="stat-card-label">Allocated</div><div className="stat-card-value" style={{ color: 'var(--success)' }}>{runResult.total_allocations}</div></div>
            <div className="stat-card"><div className="stat-card-label">Unallocated</div><div className="stat-card-value" style={{ color: 'var(--danger)' }}>{runResult.unallocated_students}</div></div>
            <div className="stat-card"><div className="stat-card-label">Avg Match Score</div><div className="stat-card-value">{runResult.avg_match_score}%</div></div>
            <div className="stat-card"><div className="stat-card-label">First Choice Rate</div><div className="stat-card-value">{runResult.first_choice_rate}%</div></div>
            <div className="stat-card"><div className="stat-card-label">Unfilled Seats</div><div className="stat-card-value">{runResult.unfilled_seats}</div></div>
            <div className="stat-card"><div className="stat-card-label">Seat Utilization</div>
              <div className="stat-card-value">{stats ? stats.seat_utilization : '—'}%</div></div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex-gap mb-3">
        {['overview', 'results', 'unallocated', 'unfilled', 'insights'].map(t => (
          <button key={t} className={`btn ${tab === t ? 'btn-primary' : 'btn-outline'} btn-sm`}
            onClick={() => setTab(t)}>{t.charAt(0).toUpperCase() + t.slice(1)}</button>
        ))}
      </div>

      {/* Tab content */}
      {tab === 'overview' && stats && (
        <div>
          <div className="stats-grid mb-3">
            <div className="stat-card"><div className="stat-card-label">Allocation Rate</div><div className="stat-card-value">{stats.allocation_percentage}%</div></div>
            <div className="stat-card"><div className="stat-card-label">Avg Match Score</div><div className="stat-card-value">{stats.avg_match_score}%</div></div>
            <div className="stat-card"><div className="stat-card-label">First Choice Rate</div><div className="stat-card-value">{stats.first_choice_rate}%</div></div>
            <div className="stat-card"><div className="stat-card-label">Seat Utilization</div><div className="stat-card-value">{stats.seat_utilization}%</div></div>
          </div>
          <div className="charts-grid">
            <div className="chart-card">
              <h3>Allocation by Location</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={locationData}>
                  <XAxis dataKey="name" fontSize={11} angle={-30} textAnchor="end" height={60} />
                  <YAxis fontSize={12} /><Tooltip />
                  <Bar dataKey="value" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-card">
              <h3>Allocation by Branch</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={branchData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                    {branchData.map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie><Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          {stats.skill_demand?.length > 0 && (
            <div className="chart-card mt-3">
              <h3>Top Skill Demand</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={stats.skill_demand} layout="vertical">
                  <XAxis type="number" fontSize={12} />
                  <YAxis type="category" dataKey="skill" width={120} fontSize={11} />
                  <Tooltip /><Bar dataKey="count" fill="var(--accent)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {tab === 'results' && (
        <div className="card"><div className="table-container">
          <table className="data-table">
            <thead><tr><th>Student</th><th>Internship</th><th>Company</th><th>Match</th><th>Status</th></tr></thead>
            <tbody>
              {results.map((a: any) => (
                <tr key={a.id}>
                  <td style={{ fontWeight: 500 }}>{a.student_name}</td>
                  <td>{a.internship_title}</td>
                  <td>{a.company_name}</td>
                  <td><span className="font-bold" style={{ color: a.match_score >= 80 ? 'var(--success)' : 'var(--warning)' }}>{Math.round(a.match_score)}%</span></td>
                  <td><span className={`badge ${a.allocation_status === 'accepted' ? 'badge-green' : a.allocation_status === 'allocated' ? 'badge-blue' : 'badge-gray'}`}>{a.allocation_status}</span></td>
                </tr>
              ))}
              {results.length === 0 && <tr><td colSpan={5} className="text-center text-muted" style={{ padding: '2rem' }}>No allocations yet. Run the allocation engine first.</td></tr>}
            </tbody>
          </table>
        </div></div>
      )}

      {tab === 'unallocated' && (
        <div className="card"><div className="table-container">
          <table className="data-table">
            <thead><tr><th>Student</th><th>Branch</th><th>College</th><th>CGPA</th><th>Location</th></tr></thead>
            <tbody>
              {unallocated.map((s: any) => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 500 }}>{s.name}</td>
                  <td><span className="badge badge-blue">{s.branch}</span></td>
                  <td>{s.college}</td>
                  <td>{s.cgpa}</td>
                  <td>{s.location}</td>
                </tr>
              ))}
              {unallocated.length === 0 && <tr><td colSpan={5} className="text-center text-muted" style={{ padding: '2rem' }}>All students allocated!</td></tr>}
            </tbody>
          </table>
        </div></div>
      )}

      {tab === 'unfilled' && (
        <div className="card"><div className="table-container">
          <table className="data-table">
            <thead><tr><th>Internship</th><th>Company</th><th>Domain</th><th>Seats</th><th>Filled</th><th>Remaining</th></tr></thead>
            <tbody>
              {unfilled.map((i: any) => (
                <tr key={i.id}>
                  <td style={{ fontWeight: 500 }}>{i.title}</td>
                  <td>{i.company_name}</td>
                  <td><span className="badge badge-blue">{i.domain}</span></td>
                  <td>{i.seats}</td>
                  <td>{i.filled}</td>
                  <td style={{ color: 'var(--danger)', fontWeight: 600 }}>{i.remaining}</td>
                </tr>
              ))}
              {unfilled.length === 0 && <tr><td colSpan={6} className="text-center text-muted" style={{ padding: '2rem' }}>All seats filled!</td></tr>}
            </tbody>
          </table>
        </div></div>
      )}

      {tab === 'insights' && stats && (
        <div>
          <h3 style={{ color: 'var(--primary)', marginBottom: '1rem' }}>🧠 AI Allocation Insights</h3>
          <div className="stats-grid">
            <div className="stat-card"><div className="stat-card-label">Total Efficiency</div>
              <div className="stat-card-value">{stats.allocation_percentage}%</div></div>
            <div className="stat-card"><div className="stat-card-label">Avg Match Score</div>
              <div className="stat-card-value">{stats.avg_match_score}%</div></div>
            <div className="stat-card"><div className="stat-card-label">First Choice %</div>
              <div className="stat-card-value">{stats.first_choice_rate}%</div></div>
            <div className="stat-card"><div className="stat-card-label">Seat Utilization</div>
              <div className="stat-card-value">{stats.seat_utilization}%</div></div>
          </div>

          {/* Fairness metrics */}
          <div className="card mt-3"><div className="card-header"><h3>📊 Fairness Metrics</h3></div>
            <div className="card-body">
              <div className="grid-2">
                <div>
                  <h4 style={{ marginBottom: '0.5rem' }}>Allocation by Gender</h4>
                  {Object.entries(stats.by_gender || {}).map(([g, c]: [string, any]) => (
                    <div key={g} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.375rem 0', borderBottom: '1px solid var(--gray-100)' }}>
                      <span>{g}</span><span className="font-bold">{c}</span>
                    </div>
                  ))}
                </div>
                <div>
                  <h4 style={{ marginBottom: '0.5rem' }}>Allocation by Domain</h4>
                  {Object.entries(stats.by_domain || {}).map(([d, c]: [string, any]) => (
                    <div key={d} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.375rem 0', borderBottom: '1px solid var(--gray-100)' }}>
                      <span>{d}</span><span className="font-bold">{c}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="chart-card mt-3">
            <h3>Geographic Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={locationData}>
                <XAxis dataKey="name" fontSize={11} angle={-30} textAnchor="end" height={60} />
                <YAxis fontSize={12} /><Tooltip />
                <Bar dataKey="value" fill="var(--accent)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
