import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { studentApi } from '../../api/client';
import { Users, Briefcase, Star, CheckCircle, ClipboardList, FileText, TrendingUp } from 'lucide-react';

export default function StudentDashboard() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [applications, setApplications] = useState<any[]>([]);
  const [allocations, setAllocations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      studentApi.getProfile().catch(() => null),
      studentApi.getRecommendations().catch(() => []),
      studentApi.getApplications().catch(() => []),
      studentApi.getAllocations().catch(() => []),
    ]).then(([p, r, a, al]) => {
      setProfile(p);
      setRecommendations(r || []);
      setApplications(a || []);
      setAllocations(al || []);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  const profileCompletion = profile ? [
    profile.degree, profile.branch, profile.college, profile.cgpa,
    profile.location, profile.phone, profile.bio,
    profile.skills?.length > 0,
  ].filter(Boolean).length / 8 * 100 : 0;

  const topMatch = recommendations[0];

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Welcome back, {user?.name}!</h2>
          <p>Here's an overview of your internship journey</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Profile Completion</span>
            <div className="stat-card-icon blue"><FileText size={20} /></div>
          </div>
          <div className="stat-card-value">{Math.round(profileCompletion)}%</div>
          <div className="score-bar" style={{ marginTop: '0.5rem' }}>
            <div className="score-bar-fill high" style={{ width: `${profileCompletion}%` }} />
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Recommendations</span>
            <div className="stat-card-icon green"><Star size={20} /></div>
          </div>
          <div className="stat-card-value">{recommendations.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Applications</span>
            <div className="stat-card-icon orange"><ClipboardList size={20} /></div>
          </div>
          <div className="stat-card-value">{applications.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Allocations</span>
            <div className="stat-card-icon purple"><CheckCircle size={20} /></div>
          </div>
          <div className="stat-card-value">{allocations.length}</div>
        </div>
      </div>

      {topMatch && (
        <div className="card mb-3">
          <div className="card-header">
            <h3>🏆 Top Match</h3>
            <Link to="/student/recommendations" className="btn btn-sm btn-outline">View All</Link>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h4 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--primary)' }}>
                  {topMatch.internship?.title}
                </h4>
                <p className="text-sm text-muted">{topMatch.internship?.company_name} • {topMatch.internship?.location}</p>
              </div>
              <div className="match-score">
                <div className={`match-score-circle ${topMatch.match?.overall_score >= 80 ? 'match-high' : topMatch.match?.overall_score >= 50 ? 'match-medium' : 'match-low'}`}>
                  {Math.round(topMatch.match?.overall_score || 0)}%
                </div>
              </div>
            </div>
            <div className="score-breakdown">
              <div className="score-item">
                <div className="score-item-label">Skills</div>
                <div className="score-item-value">{Math.round(topMatch.match?.skill_score || 0)}%</div>
              </div>
              <div className="score-item">
                <div className="score-item-label">Education</div>
                <div className="score-item-value">{Math.round(topMatch.match?.education_score || 0)}%</div>
              </div>
              <div className="score-item">
                <div className="score-item-label">Location</div>
                <div className="score-item-value">{Math.round(topMatch.match?.location_score || 0)}%</div>
              </div>
              <div className="score-item">
                <div className="score-item-label">Preference</div>
                <div className="score-item-value">{Math.round(topMatch.match?.preference_score || 0)}%</div>
              </div>
              <div className="score-item">
                <div className="score-item-label">Academic</div>
                <div className="score-item-value">{Math.round(topMatch.match?.academic_score || 0)}%</div>
              </div>
              <div className="score-item">
                <div className="score-item-label">Semantic</div>
                <div className="score-item-value">{Math.round(topMatch.match?.semantic_score || 0)}%</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {allocations.length > 0 && (
        <div className="card mb-3">
          <div className="card-header"><h3>🎯 Your Allocations</h3></div>
          <div className="card-body">
            {allocations.map((a: any) => (
              <div key={a.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 0', borderBottom: '1px solid var(--gray-100)' }}>
                <div>
                  <div style={{ fontWeight: 600 }}>{a.internship_title}</div>
                  <div className="text-sm text-muted">{a.company_name}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span className={`badge ${a.allocation_status === 'accepted' ? 'badge-green' : a.allocation_status === 'allocated' ? 'badge-blue' : 'badge-gray'}`}>
                    {a.allocation_status}
                  </span>
                  <span className="font-bold">{Math.round(a.match_score)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h3>Recent Applications</h3>
          <Link to="/student/applications" className="btn btn-sm btn-outline">View All</Link>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr><th>Internship</th><th>Company</th><th>Status</th><th>Match</th><th>Applied</th></tr>
            </thead>
            <tbody>
              {applications.slice(0, 5).map((a: any) => (
                <tr key={a.id}>
                  <td style={{ fontWeight: 500 }}>{a.internship_title}</td>
                  <td>{a.company_name}</td>
                  <td><span className={`badge ${a.status === 'pending' ? 'badge-orange' : a.status === 'shortlisted' ? 'badge-green' : 'badge-gray'}`}>{a.status}</span></td>
                  <td>{a.match_score ? `${Math.round(a.match_score)}%` : '—'}</td>
                  <td className="text-muted">{a.applied_at ? new Date(a.applied_at).toLocaleDateString() : '—'}</td>
                </tr>
              ))}
              {applications.length === 0 && (
                <tr><td colSpan={5} className="text-center text-muted" style={{ padding: '2rem' }}>No applications yet. Browse internships to apply!</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
