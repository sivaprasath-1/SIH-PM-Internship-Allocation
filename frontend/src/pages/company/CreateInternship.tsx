import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { companyApi } from '../../api/client';
import { Save } from 'lucide-react';

export default function CreateInternship() {
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    title: '', description: '', domain: '', location: '', work_mode: 'onsite',
    duration: '', stipend: '', seats: '1', minimum_cgpa: '', application_deadline: '',
    eligible_degrees: 'B.Tech, B.E., M.Tech, MCA',
    eligible_branches: '', required_skills: '', preferred_skills: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await companyApi.createInternship({
        ...form,
        stipend: form.stipend ? parseFloat(form.stipend) : null,
        seats: parseInt(form.seats),
        minimum_cgpa: form.minimum_cgpa ? parseFloat(form.minimum_cgpa) : null,
        application_deadline: form.application_deadline || null,
        eligible_degrees: form.eligible_degrees.split(',').map(s => s.trim()).filter(Boolean),
        eligible_branches: form.eligible_branches.split(',').map(s => s.trim()).filter(Boolean),
        required_skills: form.required_skills.split(',').map(s => s.trim()).filter(Boolean),
        preferred_skills: form.preferred_skills.split(',').map(s => s.trim()).filter(Boolean),
      });
      navigate('/company/internships');
    } catch (err: any) { setError(err.message); }
    finally { setSaving(false); }
  };

  return (
    <div>
      <div className="page-header"><div><h2>Create Internship</h2><p>Define a new internship opportunity</p></div></div>
      {error && <div className="error-msg mb-2">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="card mb-2"><div className="card-body">
          <h3 style={{ marginBottom: '1rem', color: 'var(--primary)' }}>Basic Information</h3>
          <div className="grid-2">
            <div className="form-group"><label>Title *</label>
              <input className="form-input" required value={form.title} onChange={e => setForm({...form, title: e.target.value})} placeholder="e.g. AI/ML Research Intern" /></div>
            <div className="form-group"><label>Domain</label>
              <select className="form-select" value={form.domain} onChange={e => setForm({...form, domain: e.target.value})}>
                <option value="">Select</option>
                <option>AI/ML</option><option>Web Development</option><option>Cybersecurity</option>
                <option>Data Science</option><option>Cloud Computing</option><option>Embedded Systems</option>
                <option>Software Engineering</option><option>IoT</option>
              </select></div>
            <div className="form-group"><label>Location</label>
              <input className="form-input" value={form.location} onChange={e => setForm({...form, location: e.target.value})} placeholder="City" /></div>
            <div className="form-group"><label>Work Mode</label>
              <select className="form-select" value={form.work_mode} onChange={e => setForm({...form, work_mode: e.target.value})}>
                <option value="onsite">On-site</option><option value="remote">Remote</option><option value="hybrid">Hybrid</option>
              </select></div>
            <div className="form-group"><label>Duration</label>
              <input className="form-input" value={form.duration} onChange={e => setForm({...form, duration: e.target.value})} placeholder="e.g. 3 months" /></div>
            <div className="form-group"><label>Stipend (₹/month)</label>
              <input type="number" className="form-input" value={form.stipend} onChange={e => setForm({...form, stipend: e.target.value})} placeholder="20000" /></div>
            <div className="form-group"><label>Number of Seats *</label>
              <input type="number" min="1" className="form-input" value={form.seats} onChange={e => setForm({...form, seats: e.target.value})} /></div>
            <div className="form-group"><label>Application Deadline</label>
              <input type="datetime-local" className="form-input" value={form.application_deadline} onChange={e => setForm({...form, application_deadline: e.target.value})} /></div>
          </div>
          <div className="form-group"><label>Description</label>
            <textarea className="form-textarea" value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Describe the internship..." /></div>
        </div></div>

        <div className="card mb-2"><div className="card-body">
          <h3 style={{ marginBottom: '1rem', color: 'var(--primary)' }}>Eligibility & Skills</h3>
          <div className="grid-2">
            <div className="form-group"><label>Minimum CGPA</label>
              <input type="number" step="0.1" className="form-input" value={form.minimum_cgpa} onChange={e => setForm({...form, minimum_cgpa: e.target.value})} placeholder="6.0" /></div>
            <div className="form-group"><label>Eligible Degrees (comma separated)</label>
              <input className="form-input" value={form.eligible_degrees} onChange={e => setForm({...form, eligible_degrees: e.target.value})} /></div>
            <div className="form-group"><label>Eligible Branches (comma separated)</label>
              <input className="form-input" value={form.eligible_branches} onChange={e => setForm({...form, eligible_branches: e.target.value})} placeholder="CSE, IT, ECE" /></div>
          </div>
          <div className="grid-2">
            <div className="form-group"><label>Required Skills (comma separated)</label>
              <input className="form-input" value={form.required_skills} onChange={e => setForm({...form, required_skills: e.target.value})} placeholder="Python, Machine Learning, SQL" /></div>
            <div className="form-group"><label>Preferred Skills (comma separated)</label>
              <input className="form-input" value={form.preferred_skills} onChange={e => setForm({...form, preferred_skills: e.target.value})} placeholder="TensorFlow, Docker" /></div>
          </div>
        </div></div>

        <button type="submit" className="btn btn-primary btn-lg" disabled={saving}>
          <Save size={16} /> {saving ? 'Creating...' : 'Create Internship'}
        </button>
      </form>
    </div>
  );
}
