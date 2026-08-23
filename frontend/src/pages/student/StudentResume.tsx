import React, { useState } from 'react';
import { studentApi } from '../../api/client';
import { Upload, FileText, CheckCircle } from 'lucide-react';

export default function StudentResume() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [msg, setMsg] = useState('');

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setMsg('');
    try {
      const result = await studentApi.uploadResume(file);
      setAnalysis(result.analysis);
      setMsg('Resume uploaded successfully!');
    } catch (err: any) {
      setMsg(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const addExtractedSkill = async (skillName: string) => {
    try {
      await studentApi.addSkill({ name: skillName, proficiency_level: 'intermediate' });
      // Remove from suggestions
      if (analysis) {
        setAnalysis({ ...analysis, skills: analysis.skills.filter((s: string) => s !== skillName) });
      }
    } catch (err: any) {
      // Skill may already exist
    }
  };

  return (
    <div>
      <div className="page-header">
        <div><h2>Resume Upload</h2><p>Upload your resume to auto-extract skills and profile data</p></div>
      </div>

      <div className="card mb-3">
        <div className="card-body">
          <div style={{ border: '2px dashed var(--border)', borderRadius: 'var(--radius-lg)', padding: '2rem', textAlign: 'center' }}>
            <Upload size={48} color="var(--gray-400)" style={{ marginBottom: '1rem' }} />
            <h3 style={{ marginBottom: '0.5rem' }}>Upload your resume</h3>
            <p className="text-sm text-muted mb-2">PDF files only, max 10MB</p>
            <input type="file" accept=".pdf" onChange={e => setFile(e.target.files?.[0] || null)}
              style={{ marginBottom: '1rem' }} />
            {file && (
              <div style={{ marginTop: '1rem' }}>
                <p className="text-sm"><FileText size={14} style={{ display: 'inline' }} /> {file.name} ({(file.size / 1024).toFixed(1)} KB)</p>
                <button className="btn btn-primary mt-2" onClick={handleUpload} disabled={uploading}>
                  {uploading ? 'Uploading & Analyzing...' : 'Upload & Analyze'}
                </button>
              </div>
            )}
          </div>
          {msg && <div className={msg.includes('success') ? 'badge badge-green' : 'error-msg'} style={{ marginTop: '1rem', padding: '0.75rem' }}>{msg}</div>}
        </div>
      </div>

      {analysis && (
        <div className="card">
          <div className="card-header"><h3>📄 Resume Analysis Results</h3></div>
          <div className="card-body">
            <p className="text-sm text-muted mb-2">Review the extracted data and confirm skills to add to your profile.</p>

            {analysis.name && (
              <div className="mb-2"><strong>Name:</strong> {analysis.name}</div>
            )}
            {analysis.degree && (
              <div className="mb-2"><strong>Degree:</strong> {analysis.degree}</div>
            )}
            {analysis.branch && (
              <div className="mb-2"><strong>Branch:</strong> {analysis.branch}</div>
            )}

            {analysis.skills?.length > 0 && (
              <div className="mt-3">
                <h4 style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.75rem' }}>Extracted Skills (click to add)</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {analysis.skills.map((skill: string) => (
                    <button key={skill} className="skill-tag" onClick={() => addExtractedSkill(skill)}
                      style={{ cursor: 'pointer', border: '1px solid var(--primary-100)' }}>
                      + {skill}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {analysis.projects?.length > 0 && (
              <div className="mt-3">
                <h4 style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.5rem' }}>Projects</h4>
                <ul style={{ paddingLeft: '1.5rem' }}>
                  {analysis.projects.map((p: string, i: number) => (
                    <li key={i} className="text-sm" style={{ marginBottom: '0.25rem' }}>{p}</li>
                  ))}
                </ul>
              </div>
            )}

            {analysis.certifications?.length > 0 && (
              <div className="mt-3">
                <h4 style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.5rem' }}>Certifications</h4>
                <ul style={{ paddingLeft: '1.5rem' }}>
                  {analysis.certifications.map((c: string, i: number) => (
                    <li key={i} className="text-sm" style={{ marginBottom: '0.25rem' }}>{c}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
