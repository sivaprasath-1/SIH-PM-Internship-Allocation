import React, { useEffect, useState } from 'react';
import { companyApi } from '../../api/client';
import { Save } from 'lucide-react';

export default function CompanyProfile() {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const [form, setForm] = useState({ organization_name: '', description: '', industry: '', location: '', website: '' });

  useEffect(() => {
    companyApi.getProfile().then(p => {
      setProfile(p);
      setForm({
        organization_name: p.organization_name || '', description: p.description || '',
        industry: p.industry || '', location: p.location || '', website: p.website || '',
      });
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await companyApi.updateProfile(form);
      setMsg('Profile saved!');
      setTimeout(() => setMsg(''), 3000);
    } catch (err: any) { setMsg(err.message); }
    finally { setSaving(false); }
  };

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div><h2>Organization Profile</h2></div>
        <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
          <Save size={16} /> {saving ? 'Saving...' : 'Save'}
        </button>
      </div>
      {msg && <div className="badge badge-green mb-2" style={{ padding: '0.75rem' }}>{msg}</div>}
      <div className="card"><div className="card-body">
        <div className="grid-2">
          <div className="form-group"><label>Organization Name</label>
            <input className="form-input" value={form.organization_name} onChange={e => setForm({...form, organization_name: e.target.value})} /></div>
          <div className="form-group"><label>Industry</label>
            <input className="form-input" value={form.industry} onChange={e => setForm({...form, industry: e.target.value})} /></div>
          <div className="form-group"><label>Location</label>
            <input className="form-input" value={form.location} onChange={e => setForm({...form, location: e.target.value})} /></div>
          <div className="form-group"><label>Website</label>
            <input className="form-input" value={form.website} onChange={e => setForm({...form, website: e.target.value})} /></div>
        </div>
        <div className="form-group"><label>Description</label>
          <textarea className="form-textarea" value={form.description} onChange={e => setForm({...form, description: e.target.value})} /></div>
        {profile?.verification_status && (
          <div className="mt-2">
            <span className={`badge ${profile.verification_status === 'verified' ? 'badge-green' : profile.verification_status === 'pending' ? 'badge-orange' : 'badge-red'}`}>
              Verification: {profile.verification_status}
            </span>
          </div>
        )}
      </div></div>
    </div>
  );
}
