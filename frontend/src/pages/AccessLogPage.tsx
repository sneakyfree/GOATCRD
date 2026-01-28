import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface AccessLogEntry {
    id: string;
    accessor_id: string | null;
    accessor_type: string;
    accessor_role: string | null;
    resource_type: string;
    resource_id: string | null;
    action: string;
    purpose: string | null;
    ip_address: string | null;
    created_at: string;
}

export function AccessLogPage() {
    const [logs, setLogs] = useState<AccessLogEntry[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>('all');
    const [exporting, setExporting] = useState(false);

    useEffect(() => {
        fetchLogs();
    }, [filter]);

    const fetchLogs = async () => {
        try {
            // Mock data for demo
            const mockLogs: AccessLogEntry[] = [
                {
                    id: 'log-001',
                    accessor_id: 'system',
                    accessor_type: 'system',
                    accessor_role: null,
                    resource_type: 'intake_data',
                    resource_id: 'case-123',
                    action: 'read',
                    purpose: 'Scenario generation',
                    ip_address: null,
                    created_at: new Date(Date.now() - 3600000).toISOString()
                },
                {
                    id: 'log-002',
                    accessor_id: 'agent-intake',
                    accessor_type: 'agent',
                    accessor_role: 'intake_specialist',
                    resource_type: 'intake_data',
                    resource_id: 'case-123',
                    action: 'read',
                    purpose: 'Validation check',
                    ip_address: null,
                    created_at: new Date(Date.now() - 7200000).toISOString()
                },
                {
                    id: 'log-003',
                    accessor_id: 'user-456',
                    accessor_type: 'user',
                    accessor_role: 'pro_user',
                    resource_type: 'scenarios',
                    resource_id: 'run-789',
                    action: 'read',
                    purpose: 'Client review',
                    ip_address: '192.168.1.100',
                    created_at: new Date(Date.now() - 86400000).toISOString()
                },
                {
                    id: 'log-004',
                    accessor_id: 'partner-abc',
                    accessor_type: 'partner',
                    accessor_role: 'api_integration',
                    resource_type: 'export',
                    resource_id: 'export-001',
                    action: 'export',
                    purpose: 'Partner data sync',
                    ip_address: '10.0.0.50',
                    created_at: new Date(Date.now() - 172800000).toISOString()
                }
            ];

            const filtered = filter === 'all'
                ? mockLogs
                : mockLogs.filter(l => l.accessor_type === filter);

            setLogs(filtered);
        } catch (error) {
            console.error('Failed to fetch access logs:', error);
        } finally {
            setLoading(false);
        }
    };

    const exportLogs = async () => {
        setExporting(true);
        try {
            // In production, would call API and download CSV
            const csv = [
                'Date,Accessor Type,Accessor Role,Resource,Action,Purpose,IP Address',
                ...logs.map(log =>
                    `${log.created_at},${log.accessor_type},${log.accessor_role || 'N/A'},${log.resource_type},${log.action},${log.purpose || 'N/A'},${log.ip_address || 'N/A'}`
                )
            ].join('\n');

            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `access-log-${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        } finally {
            setExporting(false);
        }
    };

    const getAccessorIcon = (type: string) => {
        switch (type) {
            case 'user': return '👤';
            case 'system': return '⚙️';
            case 'agent': return '🤖';
            case 'partner': return '🏢';
            default: return '❓';
        }
    };

    const getAccessorColor = (type: string) => {
        switch (type) {
            case 'user': return 'bg-blue-500/20 text-blue-300';
            case 'system': return 'bg-gray-500/20 text-gray-300';
            case 'agent': return 'bg-purple-500/20 text-purple-300';
            case 'partner': return 'bg-green-500/20 text-green-300';
            default: return 'bg-white/20 text-white';
        }
    };

    const getActionColor = (action: string) => {
        switch (action) {
            case 'read': return 'text-blue-300';
            case 'export': return 'text-green-300';
            case 'share': return 'text-yellow-300';
            case 'delete': return 'text-red-300';
            default: return 'text-white/60';
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                        <span className="text-4xl">📋</span>
                        Access Log
                    </h1>
                    <p className="text-white/60 mt-2">
                        1033-compliant record of who accessed your data, when, and why
                    </p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={exportLogs}
                        disabled={exporting}
                        className="btn-secondary flex items-center gap-2"
                    >
                        {exporting ? 'Exporting...' : '📥 Export CSV'}
                    </button>
                    <Link to="/my-data" className="btn-secondary">
                        ← Back
                    </Link>
                </div>
            </div>

            {/* Filters */}
            <div className="glass rounded-xl p-4">
                <div className="flex items-center gap-4">
                    <span className="text-white/60">Filter by accessor:</span>
                    {['all', 'user', 'system', 'agent', 'partner'].map(f => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-4 py-2 rounded-lg transition-colors capitalize ${filter === f
                                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/50'
                                : 'bg-white/5 text-white/60 hover:bg-white/10'
                                }`}
                        >
                            {f}
                        </button>
                    ))}
                </div>
            </div>

            {/* Stats Summary */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: 'Total Accesses', value: logs.length, icon: '📊' },
                    { label: 'By Users', value: logs.filter(l => l.accessor_type === 'user').length, icon: '👤' },
                    { label: 'By Agents', value: logs.filter(l => l.accessor_type === 'agent').length, icon: '🤖' },
                    { label: 'By Partners', value: logs.filter(l => l.accessor_type === 'partner').length, icon: '🏢' },
                ].map((stat, i) => (
                    <div key={i} className="glass rounded-lg p-4 text-center">
                        <span className="text-2xl">{stat.icon}</span>
                        <p className="text-2xl font-bold text-white mt-2">{stat.value}</p>
                        <p className="text-white/50 text-sm">{stat.label}</p>
                    </div>
                ))}
            </div>

            {/* Access Log Table */}
            <div className="glass rounded-xl overflow-hidden">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-white/10">
                            <th className="text-left p-4 text-white/60 font-medium">Date</th>
                            <th className="text-left p-4 text-white/60 font-medium">Accessor</th>
                            <th className="text-left p-4 text-white/60 font-medium">Resource</th>
                            <th className="text-left p-4 text-white/60 font-medium">Action</th>
                            <th className="text-left p-4 text-white/60 font-medium">Purpose</th>
                            <th className="text-left p-4 text-white/60 font-medium">IP</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logs.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="p-8 text-center text-white/40">
                                    No access logs found
                                </td>
                            </tr>
                        ) : (
                            logs.map(log => (
                                <tr key={log.id} className="border-b border-white/5 hover:bg-white/5">
                                    <td className="p-4 text-white/70">{formatDate(log.created_at)}</td>
                                    <td className="p-4">
                                        <div className="flex items-center gap-2">
                                            <span className={`px-2 py-1 rounded-full text-xs ${getAccessorColor(log.accessor_type)}`}>
                                                {getAccessorIcon(log.accessor_type)} {log.accessor_type}
                                            </span>
                                            {log.accessor_role && (
                                                <span className="text-white/40 text-xs">({log.accessor_role})</span>
                                            )}
                                        </div>
                                    </td>
                                    <td className="p-4 text-white/70">{log.resource_type}</td>
                                    <td className="p-4">
                                        <span className={getActionColor(log.action)}>{log.action}</span>
                                    </td>
                                    <td className="p-4 text-white/50 text-sm">{log.purpose || '—'}</td>
                                    <td className="p-4 text-white/40 font-mono text-sm">{log.ip_address || '—'}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* 1033 Compliance Note */}
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                <div className="flex items-start gap-3">
                    <span className="text-xl">🏛️</span>
                    <div>
                        <h3 className="text-blue-300 font-medium">1033 Compliance</h3>
                        <p className="text-white/60 text-sm mt-1">
                            This access log is maintained in accordance with CFPB 1033 requirements.
                            You have the right to know who accessed your financial data, when, and for what purpose.
                            You can export this log at any time or request deletion of your data.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default AccessLogPage;
