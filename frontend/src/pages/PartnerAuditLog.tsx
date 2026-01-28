import { useState } from 'react';
import { Link } from 'react-router-dom';

interface AuditLogEntry {
    id: string;
    partner_id: string;
    partner_name: string;
    timestamp: string;
    action: 'api_call' | 'config_change' | 'credential_rotate' | 'webhook_triggered' | 'rate_limit_hit';
    endpoint: string;
    status_code: number;
    response_time_ms: number;
    ip_address: string;
    user_agent: string;
    request_id: string;
}

const MOCK_AUDIT_LOG: AuditLogEntry[] = [
    { id: 'log-001', partner_id: 'p-001', partner_name: 'Acme Financial', timestamp: new Date(Date.now() - 60000).toISOString(), action: 'api_call', endpoint: '/api/v1/decisions', status_code: 200, response_time_ms: 145, ip_address: '192.168.1.1', user_agent: 'AcmeClient/1.0', request_id: 'req-abc123' },
    { id: 'log-002', partner_id: 'p-002', partner_name: 'Metro Credit Union', timestamp: new Date(Date.now() - 120000).toISOString(), action: 'api_call', endpoint: '/api/v1/scenarios', status_code: 200, response_time_ms: 89, ip_address: '10.0.0.5', user_agent: 'MetroAPI/2.1', request_id: 'req-def456' },
    { id: 'log-003', partner_id: 'p-001', partner_name: 'Acme Financial', timestamp: new Date(Date.now() - 300000).toISOString(), action: 'webhook_triggered', endpoint: '/webhooks/decision-complete', status_code: 200, response_time_ms: 230, ip_address: '192.168.1.1', user_agent: 'GOATCRD-Webhook/1.0', request_id: 'req-ghi789' },
    { id: 'log-004', partner_id: 'p-003', partner_name: 'First National', timestamp: new Date(Date.now() - 600000).toISOString(), action: 'rate_limit_hit', endpoint: '/api/v1/decisions', status_code: 429, response_time_ms: 5, ip_address: '172.16.0.10', user_agent: 'FirstNat/3.0', request_id: 'req-jkl012' },
    { id: 'log-005', partner_id: 'p-002', partner_name: 'Metro Credit Union', timestamp: new Date(Date.now() - 900000).toISOString(), action: 'credential_rotate', endpoint: '/admin/api-keys/rotate', status_code: 200, response_time_ms: 312, ip_address: '10.0.0.5', user_agent: 'MetroAdmin/1.0', request_id: 'req-mno345' },
    { id: 'log-006', partner_id: 'p-001', partner_name: 'Acme Financial', timestamp: new Date(Date.now() - 1800000).toISOString(), action: 'config_change', endpoint: '/admin/partner/p-001/settings', status_code: 200, response_time_ms: 178, ip_address: '192.168.1.1', user_agent: 'AcmeAdmin/1.0', request_id: 'req-pqr678' },
];

export default function PartnerAuditLog() {
    const [logs] = useState<AuditLogEntry[]>(MOCK_AUDIT_LOG);
    const [partnerFilter, setPartnerFilter] = useState<string>('all');
    const [actionFilter, setActionFilter] = useState<string>('all');
    const [selectedLog, setSelectedLog] = useState<AuditLogEntry | null>(null);

    const partners = [...new Set(logs.map(l => l.partner_name))];
    const actions = [...new Set(logs.map(l => l.action))];

    const filteredLogs = logs.filter(log => {
        if (partnerFilter !== 'all' && log.partner_name !== partnerFilter) return false;
        if (actionFilter !== 'all' && log.action !== actionFilter) return false;
        return true;
    });

    const getActionColor = (action: string) => {
        switch (action) {
            case 'api_call': return 'bg-blue-500/20 text-blue-400';
            case 'config_change': return 'bg-purple-500/20 text-purple-400';
            case 'credential_rotate': return 'bg-orange-500/20 text-orange-400';
            case 'webhook_triggered': return 'bg-green-500/20 text-green-400';
            case 'rate_limit_hit': return 'bg-red-500/20 text-red-400';
            default: return 'bg-white/20 text-white/60';
        }
    };

    const getStatusColor = (code: number) => {
        if (code >= 200 && code < 300) return 'text-green-400';
        if (code >= 400 && code < 500) return 'text-yellow-400';
        return 'text-red-400';
    };

    const formatTimestamp = (ts: string) => {
        return new Date(ts).toLocaleString('en-US', {
            month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit'
        });
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                        <span className="text-4xl">📋</span>
                        Partner Audit Log
                    </h1>
                    <p className="text-white/60 mt-2">
                        Complete API activity and configuration change history
                    </p>
                </div>
                <div className="flex gap-3">
                    <button className="btn-secondary">
                        📥 Export CSV
                    </button>
                    <Link to="/admin/partners" className="btn-secondary">
                        ← Back to Partners
                    </Link>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="glass rounded-xl p-4">
                    <div className="text-2xl font-bold text-white">{logs.length}</div>
                    <div className="text-white/60 text-sm">Total Events</div>
                </div>
                <div className="glass rounded-xl p-4">
                    <div className="text-2xl font-bold text-blue-400">
                        {logs.filter(l => l.action === 'api_call').length}
                    </div>
                    <div className="text-white/60 text-sm">API Calls</div>
                </div>
                <div className="glass rounded-xl p-4">
                    <div className="text-2xl font-bold text-green-400">
                        {logs.filter(l => l.status_code >= 200 && l.status_code < 300).length}
                    </div>
                    <div className="text-white/60 text-sm">Successful</div>
                </div>
                <div className="glass rounded-xl p-4">
                    <div className="text-2xl font-bold text-red-400">
                        {logs.filter(l => l.action === 'rate_limit_hit').length}
                    </div>
                    <div className="text-white/60 text-sm">Rate Limited</div>
                </div>
                <div className="glass rounded-xl p-4">
                    <div className="text-2xl font-bold text-white">
                        {Math.round(logs.reduce((acc, l) => acc + l.response_time_ms, 0) / logs.length)}ms
                    </div>
                    <div className="text-white/60 text-sm">Avg Response</div>
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-4">
                <div>
                    <label className="text-white/60 text-sm block mb-1">Partner</label>
                    <select
                        value={partnerFilter}
                        onChange={e => setPartnerFilter(e.target.value)}
                        className="bg-white/10 text-white border border-white/20 rounded-lg px-4 py-2"
                    >
                        <option value="all">All Partners</option>
                        {partners.map(p => (
                            <option key={p} value={p}>{p}</option>
                        ))}
                    </select>
                </div>
                <div>
                    <label className="text-white/60 text-sm block mb-1">Action</label>
                    <select
                        value={actionFilter}
                        onChange={e => setActionFilter(e.target.value)}
                        className="bg-white/10 text-white border border-white/20 rounded-lg px-4 py-2"
                    >
                        <option value="all">All Actions</option>
                        {actions.map(a => (
                            <option key={a} value={a}>{a.replace('_', ' ')}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Log Table */}
            <div className="glass rounded-xl overflow-hidden">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-white/10">
                            <th className="text-left text-white/60 text-sm font-medium p-4">Timestamp</th>
                            <th className="text-left text-white/60 text-sm font-medium p-4">Partner</th>
                            <th className="text-left text-white/60 text-sm font-medium p-4">Action</th>
                            <th className="text-left text-white/60 text-sm font-medium p-4">Endpoint</th>
                            <th className="text-left text-white/60 text-sm font-medium p-4">Status</th>
                            <th className="text-left text-white/60 text-sm font-medium p-4">Latency</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredLogs.map(log => (
                            <tr
                                key={log.id}
                                onClick={() => setSelectedLog(log)}
                                className={`border-b border-white/5 cursor-pointer transition-colors ${selectedLog?.id === log.id ? 'bg-purple-500/20' : 'hover:bg-white/5'
                                    }`}
                            >
                                <td className="p-4 text-white/60 text-sm font-mono">
                                    {formatTimestamp(log.timestamp)}
                                </td>
                                <td className="p-4 text-white">{log.partner_name}</td>
                                <td className="p-4">
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${getActionColor(log.action)}`}>
                                        {log.action.replace('_', ' ')}
                                    </span>
                                </td>
                                <td className="p-4 text-white/60 font-mono text-sm">{log.endpoint}</td>
                                <td className={`p-4 font-medium ${getStatusColor(log.status_code)}`}>
                                    {log.status_code}
                                </td>
                                <td className="p-4 text-white/60">{log.response_time_ms}ms</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Log Detail Modal */}
            {selectedLog && (
                <div className="glass rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-white">Log Details</h3>
                        <button onClick={() => setSelectedLog(null)} className="text-white/60 hover:text-white">
                            ✕
                        </button>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span className="text-white/50">Request ID:</span>
                            <span className="text-white ml-2 font-mono">{selectedLog.request_id}</span>
                        </div>
                        <div>
                            <span className="text-white/50">Partner ID:</span>
                            <span className="text-white ml-2 font-mono">{selectedLog.partner_id}</span>
                        </div>
                        <div>
                            <span className="text-white/50">IP Address:</span>
                            <span className="text-white ml-2 font-mono">{selectedLog.ip_address}</span>
                        </div>
                        <div>
                            <span className="text-white/50">User Agent:</span>
                            <span className="text-white ml-2">{selectedLog.user_agent}</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
