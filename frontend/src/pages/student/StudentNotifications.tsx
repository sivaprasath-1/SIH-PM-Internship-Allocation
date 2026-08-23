import React, { useEffect, useState } from 'react';
import { notificationApi } from '../../api/client';
import { Bell, CheckCircle, Info, AlertTriangle, XCircle, Briefcase, Star } from 'lucide-react';

const typeIcons: Record<string, any> = {
  info: { icon: Info, color: 'var(--info)', bg: 'var(--info-light)' },
  success: { icon: CheckCircle, color: 'var(--success)', bg: 'var(--success-light)' },
  warning: { icon: AlertTriangle, color: 'var(--warning)', bg: 'var(--warning-light)' },
  error: { icon: XCircle, color: 'var(--danger)', bg: 'var(--danger-light)' },
  application: { icon: Briefcase, color: 'var(--info)', bg: 'var(--info-light)' },
  allocation: { icon: CheckCircle, color: 'var(--success)', bg: 'var(--success-light)' },
  recommendation: { icon: Star, color: 'var(--warning)', bg: 'var(--warning-light)' },
};

export default function StudentNotifications() {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    notificationApi.list().then(setNotifications).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const markRead = async (id: number) => {
    await notificationApi.markRead(id);
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
  };

  const markAllRead = async () => {
    await notificationApi.markAllRead();
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
  };

  if (loading) return <div className="loading-container"><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div><h2>Notifications</h2><p>Stay updated on your applications and allocations</p></div>
        {notifications.some(n => !n.is_read) && (
          <button className="btn btn-outline btn-sm" onClick={markAllRead}>Mark all as read</button>
        )}
      </div>

      <div className="card">
        {notifications.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon"><Bell size={28} /></div>
            <h3>No notifications</h3><p>You're all caught up!</p>
          </div>
        ) : (
          <ul className="notification-list">
            {notifications.map(n => {
              const typeInfo = typeIcons[n.type] || typeIcons.info;
              const Icon = typeInfo.icon;
              return (
                <li key={n.id} className={`notification-item ${!n.is_read ? 'unread' : ''}`}
                  onClick={() => !n.is_read && markRead(n.id)} style={{ cursor: !n.is_read ? 'pointer' : 'default' }}>
                  <div className="notification-icon" style={{ background: typeInfo.bg, color: typeInfo.color }}>
                    <Icon size={18} />
                  </div>
                  <div className="notification-content">
                    <div className="notification-title">{n.title}</div>
                    <div className="notification-message">{n.message}</div>
                    <div className="notification-time">{n.created_at ? new Date(n.created_at).toLocaleString() : ''}</div>
                  </div>
                  {!n.is_read && <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--info)', flexShrink: 0 }} />}
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
