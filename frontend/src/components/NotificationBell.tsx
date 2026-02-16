import { useState } from 'react';
import { Link } from 'react-router-dom';

interface Notification {
    id: string;
    type: string;
    title: string;
    message: string;
    is_read: boolean;
    created_at: string;
}

export default function NotificationBell() {
    const [open, setOpen] = useState(false);
    const [notifications] = useState<Notification[]>([
        {
            id: '1',
            type: 'pulse_alert',
            title: 'Score Change Detected',
            message: 'Your credit score increased by 12 points.',
            is_read: false,
            created_at: new Date().toISOString(),
        },
        {
            id: '2',
            type: 'system',
            title: 'Scenarios Updated',
            message: 'New lending scenarios are available.',
            is_read: false,
            created_at: new Date(Date.now() - 3600000).toISOString(),
        },
        {
            id: '3',
            type: 'consent',
            title: 'Consent Expiring',
            message: 'Your Plaid consent expires in 7 days.',
            is_read: true,
            created_at: new Date(Date.now() - 86400000).toISOString(),
        },
    ]);

    const unreadCount = notifications.filter(n => !n.is_read).length;

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

    const timeAgo = (dateStr: string) => {
        const diff = Date.now() - new Date(dateStr).getTime();
        const mins = Math.floor(diff / 60000);
        if (mins < 1) return 'just now';
        if (mins < 60) return `${mins}m ago`;
        const hours = Math.floor(mins / 60);
        if (hours < 24) return `${hours}h ago`;
        return `${Math.floor(hours / 24)}d ago`;
    };

    return (
        <div className="relative">
            <button
                onClick={() => setOpen(!open)}
                className="relative p-2 text-white/70 hover:text-white transition-colors"
                aria-label="Notifications"
            >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                    fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                </svg>
                {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-[10px] font-bold
                        w-4 h-4 flex items-center justify-center rounded-full animate-pulse">
                        {unreadCount}
                    </span>
                )}
            </button>

            {open && (
                <>
                    <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
                    <div className="absolute right-0 top-full mt-2 w-80 glass rounded-xl border border-white/10
                        shadow-2xl z-50 overflow-hidden">
                        <div className="flex items-center justify-between p-3 border-b border-white/10">
                            <span className="text-sm font-semibold text-white">Notifications</span>
                            <Link
                                to="/notifications"
                                className="text-xs text-accent-blue hover:underline"
                                onClick={() => setOpen(false)}
                            >
                                View All →
                            </Link>
                        </div>
                        <div className="max-h-72 overflow-y-auto">
                            {notifications.slice(0, 5).map(n => (
                                <div
                                    key={n.id}
                                    className={`p-3 border-b border-white/5 hover:bg-white/5 transition-colors
                                        ${!n.is_read ? 'bg-accent-blue/5' : ''}`}
                                >
                                    <div className="flex items-start gap-2">
                                        <span className="text-base mt-0.5">{getTypeIcon(n.type)}</span>
                                        <div className="flex-1 min-w-0">
                                            <p className={`text-sm ${n.is_read ? 'text-white/70' : 'text-white font-medium'}`}>
                                                {n.title}
                                            </p>
                                            <p className="text-xs text-white/50 mt-0.5 truncate">{n.message}</p>
                                            <span className="text-xs text-white/30 mt-1 block">
                                                {timeAgo(n.created_at)}
                                            </span>
                                        </div>
                                        {!n.is_read && (
                                            <span className="w-2 h-2 bg-accent-blue rounded-full mt-1.5 shrink-0" />
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
