import React, { useEffect, useState } from 'react';
import { studentApi } from '../../api/client';
import { Star, MapPin, Clock, IndianRupee, ChevronDown, ChevronUp } from 'lucide-react';

export default function StudentRecommendations() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    studentApi.getRecommendations()
      .then(setRecommendations)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div><h2>AI Recommendations</h2><p>Internships matched to your profile using AI</p></div>
      </div>

      {recommendations.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon"><Star size={28} /></div>
          <h3>No recommendations yet</h3>
          <p>Complete your profile and add skills to get AI-powered recommendations</p>
        </div>
      ) : (
        <div>
          {recommendations.map((rec: any, idx: number) => {
            const i = rec.internship;
            const m = rec.match;
            const isExpanded = expanded === idx;

            return (
              <div key={idx} className="internship-card mb-2">
                <div className="internship-card-header">
                  <div>
                    <div className="internship-card-title">{i?.title}</div>
                    <div className="internship-card-company">{i?.company_name}</div>
                  </div>
                  <div className="match-score">
                    <div className={`match-score-circle ${(m?.overall_score || 0) >= 80 ? 'match-high' : (m?.overall_score || 0) >= 50 ? 'match-medium' : 'match-low'}`}>
                      {Math.round(m?.overall_score || 0)}%
                    </div>
                  </div>
                </div>

                <div className="internship-card-meta">
                  <span><MapPin size={14} /> {i?.location || 'Remote'}</span>
                  <span><Clock size={14} /> {i?.duration}</span>
                  <span><IndianRupee size={14} /> ₹{i?.stipend?.toLocaleString()}/mo</span>
                </div>

                <div className="score-breakdown">
                  <div className="score-item">
                    <div className="score-item-label">Skills</div>
                    <div className="score-item-value">{Math.round(m?.skill_score || 0)}%</div>
                  </div>
                  <div className="score-item">
                    <div className="score-item-label">Education</div>
                    <div className="score-item-value">{Math.round(m?.education_score || 0)}%</div>
                  </div>
                  <div className="score-item">
                    <div className="score-item-label">Location</div>
                    <div className="score-item-value">{Math.round(m?.location_score || 0)}%</div>
                  </div>
                  <div className="score-item">
                    <div className="score-item-label">Preference</div>
                    <div className="score-item-value">{Math.round(m?.preference_score || 0)}%</div>
                  </div>
                  <div className="score-item">
                    <div className="score-item-label">Academic</div>
                    <div className="score-item-value">{Math.round(m?.academic_score || 0)}%</div>
                  </div>
                  <div className="score-item">
                    <div className="score-item-label">Semantic</div>
                    <div className="score-item-value">{Math.round(m?.semantic_score || 0)}%</div>
                  </div>
                </div>

                <button className="btn btn-ghost btn-sm mt-2" onClick={() => setExpanded(isExpanded ? null : idx)}>
                  {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  {isExpanded ? 'Hide Details' : 'Why this match?'}
                </button>

                {isExpanded && (
                  <div className="explanation-box">
                    <h4>Why this internship was recommended:</h4>
                    {m?.explanation?.length > 0 ? (
                      <ul className="explanation-list">
                        {m.explanation.map((r: string, j: number) => <li key={j}>{r}</li>)}
                      </ul>
                    ) : (
                      <p className="text-sm text-muted">Based on overall profile compatibility</p>
                    )}
                    {m?.skill_gaps?.length > 0 && (
                      <>
                        <h4 style={{ marginTop: '0.75rem', color: 'var(--danger)' }}>Skill Gaps:</h4>
                        <ul className="explanation-list skill-gap-list">
                          {m.skill_gaps.map((g: string, j: number) => <li key={j}>{g}</li>)}
                        </ul>
                      </>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
