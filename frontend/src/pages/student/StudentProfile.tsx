import React, { useEffect, useState } from 'react';
import { studentApi } from '../../api/client';
import { Save, Plus, X, User } from 'lucide-react';

export default function StudentProfile() {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const [newSkill, setNewSkill] = useState('');
  const [skillLevel, setSkillLevel] = useState('intermediate');

  const [form, setForm] = useState({
    phone: '', gender: '', education_level: '', degree: '', branch: '',
    college: '', graduation_year: '', cgpa: '', location: '', bio: '',
    preferred_locations: '', preferred_domains: '',
  });

  useEffect(() => {
    studentApi.getProfile().then(p => {
      setProfile(p);
      setForm({
        phone: p.phone || '', gender: p.gender || '', education_level: p.education_level || 'Undergraduate',
        degree: p.degree || '', branch: p.branch || '', college: p.college || '',
        graduation_year: p.graduation_year?.toString() || '', cgpa: p.cgpa?.toString() || '',
        location: p.location || '', bio: p.bio || '',
        preferred_locations: (p.preferred_locations || []).join(', '),
        preferred_domains: (p.preferred_domains || []).join(', '),
      });
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMsg('');
    try {
      const data: any = { ...form };
      data.graduation_year = data.graduation_year ? parseInt(data.graduation_year) : null;
      data.cgpa = data.cgpa ? parseFloat(data.cgpa) : null;
      data.preferred_locations = data.preferred_locations.split(',').map((s: string) => s.trim()).filter(Boolean);
      data.preferred_domains = data.preferred_domains.split(',').map((s: string) => s.trim()).filter(Boolean);
      const updated = await studentApi.updateProfile(data);
      setProfile(updated);
      setMsg('Profile saved successfully!');
      setTimeout(() => setMsg(''), 3000);
    } catch (err: any) {
      setMsg(err.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const addSkill = async () => {
    if (!newSkill.trim()) return;
    try {
      await studentApi.addSkill({ name: newSkill.trim(), proficiency_level: skillLevel });
      const p = await studentApi.getProfile();
      setProfile(p);
      setNewSkill('');
    } catch (err: any) {
      alert(err.message);
    }
  };

  const removeSkill = async (skillId: number) => {
    try {
      await studentApi.removeSkill(skillId);
      const p = await studentApi.getProfile();
      setProfile(p);
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div><h2>My Profile</h2><p>Complete your profile to get better recommendations</p></div>
        <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
          <Save size={16} /> {saving ? 'Saving...' : 'Save Profile'}
        </button>
      </div>

      {msg && <div className={msg.includes('success') ? 'badge badge-green' : 'error-msg'} style={{ marginBottom: '1rem', padding: '0.75rem' }}>{msg}</div>}

      <div className="profile-grid">
        <div>
          <div className="profile-section">
            <h3>Personal Information</h3>
            <div className="grid-2">
              <div className="form-group">
                <label>Phone</label>
                <input className="form-input" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} placeholder="+91 XXXXX XXXXX" />
              </div>
              <div className="form-group">
                <label>Gender</label>
                <select className="form-select" value={form.gender} onChange={e => setForm({...form, gender: e.target.value})}>
                  <option value="">Select</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="form-group">
                <label>Location</label>
                <input className="form-input" value={form.location} onChange={e => setForm({...form, location: e.target.value})} placeholder="City" />
              </div>
            </div>
            <div className="form-group">
              <label>Bio</label>
              <textarea className="form-textarea" value={form.bio} onChange={e => setForm({...form, bio: e.target.value})} placeholder="Tell us about yourself..." />
            </div>
          </div>

          <div className="profile-section">
            <h3>Education</h3>
            <div className="grid-2">
              <div className="form-group">
                <label>Degree</label>
                <select className="form-select" value={form.degree} onChange={e => setForm({...form, degree: e.target.value})}>
                  <option value="">Select</option>
                  <option value="B.Tech">B.Tech</option>
                  <option value="B.E.">B.E.</option>
                  <option value="M.Tech">M.Tech</option>
                  <option value="MCA">MCA</option>
                  <option value="B.Sc">B.Sc</option>
                  <option value="M.Sc">M.Sc</option>
                </select>
              </div>
              <div className="form-group">
                <label>Branch</label>
                <select className="form-select" value={form.branch} onChange={e => setForm({...form, branch: e.target.value})}>
                  <option value="">Select</option>
                  <option value="CSE">CSE</option><option value="IT">IT</option>
                  <option value="ECE">ECE</option><option value="EEE">EEE</option>
                  <option value="Mechanical">Mechanical</option><option value="Civil">Civil</option>
                </select>
              </div>
              <div className="form-group">
                <label>College</label>
                <input className="form-input" value={form.college} onChange={e => setForm({...form, college: e.target.value})} placeholder="College name" />
              </div>
              <div className="form-group">
                <label>Graduation Year</label>
                <input type="number" className="form-input" value={form.graduation_year} onChange={e => setForm({...form, graduation_year: e.target.value})} placeholder="2025" />
              </div>
              <div className="form-group">
                <label>CGPA (out of 10)</label>
                <input type="number" step="0.1" className="form-input" value={form.cgpa} onChange={e => setForm({...form, cgpa: e.target.value})} placeholder="8.5" />
              </div>
            </div>
          </div>

          <div className="profile-section">
            <h3>Preferences</h3>
            <div className="form-group">
              <label>Preferred Locations (comma separated)</label>
              <input className="form-input" value={form.preferred_locations} onChange={e => setForm({...form, preferred_locations: e.target.value})} placeholder="Mumbai, Bangalore, Delhi" />
            </div>
            <div className="form-group">
              <label>Preferred Domains (comma separated)</label>
              <input className="form-input" value={form.preferred_domains} onChange={e => setForm({...form, preferred_domains: e.target.value})} placeholder="AI/ML, Web Development, Data Science" />
            </div>
          </div>
        </div>

        <div>
          <div className="profile-section">
            <h3>Skills ({profile?.skills?.length || 0})</h3>
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
              <input className="form-input" value={newSkill} onChange={e => setNewSkill(e.target.value)}
                placeholder="Add a skill..." onKeyDown={e => e.key === 'Enter' && addSkill()} />
              <select className="form-select" value={skillLevel} onChange={e => setSkillLevel(e.target.value)} style={{ width: '130px' }}>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="expert">Expert</option>
              </select>
              <button className="btn btn-primary btn-sm" onClick={addSkill}><Plus size={16} /></button>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
              {profile?.skills?.map((s: any) => (
                <span key={s.id} className="skill-tag" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  {s.skill_name}
                  <button onClick={() => removeSkill(s.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
                    <X size={12} />
                  </button>
                </span>
              ))}
              {(!profile?.skills || profile.skills.length === 0) && (
                <p className="text-sm text-muted">No skills added yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
