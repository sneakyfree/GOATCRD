import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface Notification {
    id: string;
    type: string;
    title: string;
    message: string;
    is_read: boolean;
    created_at: string;
    metadata: Record<string, unknown>;
}

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

export default function NotificationsPage() {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<'all' | 'unread'>('all');
    const [typeFilter, setTypeFilter] = useState<string>('');

    useEffect(() => {
        fetchNotifications();
    }, [filter, typeFilter]);

    const fetchNotifications = async () => {
        try {
            const params = new URLSearchParams();
            if (filter === 'unread') params.set('unread', 'true');
            if (typeFilter) params.set('type', typeFilter);
            params.set('limit', '50');

            const res = await fetch(`${API_URL}/notifications?${params}`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('goatcrd_token')}` },
            });
            if (res.ok) {
                const data = await res.json();
                setNotifications(data.notifications || []);
            }
        } catch {
            // Fallback sample
            setNotifications([
                { id: '1', type: 'pulse_alert', title: 'Score Change Detected', message: 'Your credit score increased by 12 points. New scenarios may be available.', is_read: false, created_at: new Date().toISOString(), metadata: {} },
                { id: '2', type: 'system', title: 'Scenarios Updated', message: 'New lending scenarios are available based on your updated credit profile.', is_read: false, created_at: new Date(Date.now() - 3600000).toISOString(), metadata: {} },
                { id: '3', type: 'consent', title: 'Consent Expiring', message: 'Your Plaid data consent expires in 7 days. Renew to continue monitoring.', is_read: true, created_at: new Date(Date.now() - 86400000).toISOString(), metadata: {} },
                { id: '4', type: 'review', title: 'Review Complete', message: 'Your case review has been completed by the compliance team.', is_read: true, created_at: new Date(Date.now() - 172800000).toISOString(), metadata: {} },
                { id: '5', type: 'agent', title: 'Coach Suggestion', message: 'Paying down your credit card to below 30% utilization could improve your score by ~15pts.', is_read: true, created_at: new Date(Date.now() - 259200000).toISOString(), metadata: {} },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const markRead = async (id: string) => {
        try {
            await fetch(`${API_URL}/notifications/${id}/read`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${localStorage.getItem('goatcrd_token')}` },
            });
        } catch { /* ignore */ }
        setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
    };

    const markAllRead = async () => {
        try {
            await fetch(`${API_URL}/notifications/read-all`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${localStorage.getItem('goatcrd_token')}` },
            });
        } catch { /* ignore */ }
        setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    };

    const getTypeIcon = (type: string) => {
        switch (type) {
            case 'pulse_alert': return '📊';
            case 'system': return '⚙️';
            case 'consent': return '🔐';
            case 'review': return '👁️';
            case 'agent': return '🤖';
            default: return '🔔';
        }
    };

    const getTypeBadge = (type: string) => {
        switch (type) {
            case 'pulse_alert': return 'bg-blue-500/10 text-blue-400';
            case 'system': return 'bg-white/5 text-white/60';
            case 'consent': return 'bg-purple-500/10 text-purple-400';
            case 'review': return 'bg-amber-500/10 text-amber-400';
            case 'agent': return 'bg-emerald-500/10 text-emerald-400';
            default: return 'bg-white/5 text-white/60';
        }
    };

    const formatDate = (dateStr: string) => {
        const d = new Date(dateStr);
        const now = new Date();
        const diff = now.getTime() - d.getTime();
        const mins = Math.floor(diff / 60000);
        if (mins < 1) return 'Just now';
        if (mins < 60) return `${mins}m ago`;
        const hours = Math.floor(mins / 60);
        if (hours < 24) return `${hours}h ago`;
        const days = Math.floor(hours / 24);
        if (days < 7) return `${days}d ago`;
        return d.toLocaleDateString();
    };

    const unreadCount = notifications.filter(n => !n.is_read).length;
    const types = ['pulse_alert', 'system', 'consent', 'review', 'agent'];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3">
                    <Link to="/dashboard" className="text-white/50 hover:text-white text-sm">← Dashboard</Link>
                    <h1 className="text-2xl font-bold text-white">🔔 Notifications</h1>
                    {unreadCount > 0 && (
                        <span className="bg-red-500/20 text-red-400 text-xs px-2 py-0.5 rounded-full font-medium">
                            {unreadCount} unread
                        </span>
                    )}
                </div>
                {unreadCount > 0 && (
                    <button onClick={markAllRead} className="btn-secondary text-xs">
                        Mark all read
                    </button>
                )}
            </div>

            {/* Filters */}
            <div className="flex items-center gap-3 flex-wrap">
                <div className="flex gap-1 glass rounded-lg p-1">
                    {(['all', 'unread'] as const).map(f => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-3 py-1 text-xs rounded-md font-medium transition-colors ${filter === f ? 'bg-accent-blue text-white' : 'text-white/60 hover:text-white'
                                }`}
                        >
                            {f === 'all' ? 'All' : 'Unread'}
                        </button>
                    ))}
                </div>
                <div className="flex gap-1 glass rounded-lg p-1">
                    <button
                        onClick={() => setTypeFilter('')}
                        className={`px-3 py-1 text-xs rounded-md font-medium transition-colors ${!typeFilter ? 'bg-accent-blue text-white' : 'text-white/60 hover:text-white'
                            }`}
                    >
                        All Types
                    </button>
                    {types.map(t => (
                        <button
                            key={t}
                            onClick={() => setTypeFilter(t)}
                            className={`px-3 py-1 text-xs rounded-md font-medium transition-colors ${typeFilter === t ? 'bg-accent-blue text-white' : 'text-white/60 hover:text-white'
                                }`}
                        >
                            {getTypeIcon(t)} {t.replace('_', ' ')}
                        </button>
                    ))}
                </div>
            </div>

            {/* Notification List */}
            {loading ? (
                <div className="space-y-3">
                    {[1, 2, 3, 4, 5].map(i => (
                        <div key={i} className="glass rounded-xl p-4 border border-white/10 animate-pulse">
                            <div className="h-4 bg-white/10 rounded w-48 mb-2" />
                            <div className="h-3 bg-white/5 rounded w-full" />
                        </div>
                    ))}
                </div>
            ) : notifications.length === 0 ? (
                <div className="glass rounded-xl p-12 border border-white/10 text-center">
                    <span className="text-4xl mb-3 block">📭</span>
                    <p className="text-white/60">No notifications yet.</p>
                    <p className="text-white/40 text-sm mt-1">Activity updates will appear here.</p>
                </div>
            ) : (
                <div className="space-y-2">
                    {notifications.map(n => (
                        <div
                            key={n.id}
                            onClick={() => !n.is_read && markRead(n.id)}
                            className={`glass rounded-xl p-4 border transition-all cursor-pointer group ${n.is_read
                                    ? 'border-white/5 opacity-70 hover:opacity-100'
                                    : 'border-accent-blue/20 bg-accent-blue/5 hover:bg-accent-blue/10'
                                }`}
                        >
                            <div className="flex items-start gap-3">
                                <span className="text-xl mt-0.5">{getTypeIcon(n.type)}</span>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={`text-sm font-medium ${n.is_read ? 'text-white/70' : 'text-white'}`}>
                                            {n.title}
                                        </span>
                                        <span className={`text-[10px] px-1.5 py-0.5 rounded-full uppercase tracking-wider ${getTypeBadge(n.type)}`}>
                                            {n.type.replace('_', ' ')}
                                        </span>
                                    </div>
                                    <p className="text-sm text-white/60">{n.message}</p>
                                    <span className="text-xs text-white/30 mt-1 block">{formatDate(n.created_at)}</span>
                                </div>
                                {!n.is_read && (
                                    <span className="w-2.5 h-2.5 bg-accent-blue rounded-full mt-2 shrink-0" />
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
