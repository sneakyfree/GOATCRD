import { useState, useMemo } from 'react';

// Types
interface Partner {
    id: string;
    name: string;
    status: 'active' | 'pending' | 'suspended';
    allowed_programs: string[];
    branding: {
        logo_url?: string;
        primary_color?: string;
        secondary_color?: string;
    };
    callback_urls: {
        webhook?: string;
        redirect?: string;
    };
    api_key_prefix: string;
    request_count: number;
    last_active: string;
    created_at: string;
}

interface AuditLogEntry {
    id: string;
    partner_id: string;
    action: string;
    endpoint: string;
    status_code: number;
    timestamp: string;
}

// Mock data
const MOCK_PARTNERS: Partner[] = [
    {
        id: '1',
        name: 'FinanceHub Inc.',
        status: 'active',
        allowed_programs: ['1', '2'],
        branding: {
            logo_url: '/logos/financehub.png',
            primary_color: '#4f46e5',
            secondary_color: '#818cf8',
        },
        callback_urls: {
            webhook: 'https://api.financehub.com/webhooks/goatcrd',
            redirect: 'https://app.financehub.com/credit-results',
        },
        api_key_prefix: 'fh_live_',
        request_count: 12450,
        last_active: '2026-01-27T22:30:00Z',
        created_at: '2025-06-15T10:00:00Z',
    },
    {
        id: '2',
        name: 'CreditWise Partners',
        status: 'active',
        allowed_programs: ['1', '2', '3'],
        branding: {
            primary_color: '#059669',
        },
        callback_urls: {
            webhook: 'https://api.creditwise.io/hooks/credit',
        },
        api_key_prefix: 'cw_live_',
        request_count: 8230,
        last_active: '2026-01-27T21:45:00Z',
        created_at: '2025-09-01T08:00:00Z',
    },
    {
        id: '3',
        name: 'LoanConnect Demo',
        status: 'pending',
        allowed_programs: ['2'],
        branding: {},
        callback_urls: {},
        api_key_prefix: 'lc_test_',
        request_count: 156,
        last_active: '2026-01-20T14:00:00Z',
        created_at: '2026-01-10T12:00:00Z',
    },
];

const MOCK_AUDIT_LOG: AuditLogEntry[] = [
    { id: '1', partner_id: '1', action: 'CREATE_CASE', endpoint: '/partners/1/cases', status_code: 201, timestamp: '2026-01-27T22:30:00Z' },
    { id: '2', partner_id: '1', action: 'GET_SCENARIOS', endpoint: '/partners/1/scenarios/abc123', status_code: 200, timestamp: '2026-01-27T22:29:30Z' },
    { id: '3', partner_id: '2', action: 'CREATE_CASE', endpoint: '/partners/2/cases', status_code: 201, timestamp: '2026-01-27T21:45:00Z' },
    { id: '4', partner_id: '1', action: 'EXPORT', endpoint: '/partners/1/exports', status_code: 200, timestamp: '2026-01-27T21:30:00Z' },
    { id: '5', partner_id: '2', action: 'CREATE_CASE', endpoint: '/partners/2/cases', status_code: 400, timestamp: '2026-01-27T20:15:00Z' },
];

const MOCK_PROGRAMS = [
    { id: '1', name: 'Prime Rewards Card' },
    { id: '2', name: 'FlexLoan Personal' },
    { id: '3', name: 'HomePath Mortgage' },
    { id: '4', name: 'AutoEase Finance' },
];

export default function AdminPartnersPage() {
    const [partners, setPartners] = useState<Partner[]>(MOCK_PARTNERS);
    const [selectedPartner, setSelectedPartner] = useState<Partner | null>(null);
    const [showForm, setShowForm] = useState(false);
    const [showAuditLog, setShowAuditLog] = useState(false);
    const [filter, setFilter] = useState<'all' | 'active' | 'pending' | 'suspended'>('all');

    const filteredPartners = useMemo(() =>
        filter === 'all' ? partners : partners.filter(p => p.status === filter),
        [partners, filter]);

    const totalRequests = useMemo(() =>
        partners.reduce((sum, p) => sum + p.request_count, 0),
        [partners]);

    const handleCreate = () => {
        setSelectedPartner({
            id: '',
            name: '',
            status: 'pending',
            allowed_programs: [],
            branding: {},
            callback_urls: {},
            api_key_prefix: '',
            request_count: 0,
            last_active: new Date().toISOString(),
            created_at: new Date().toISOString(),
        });
        setShowForm(true);
    };

    const handleEdit = (partner: Partner) => {
        setSelectedPartner(partner);
        setShowForm(true);
    };

    const handleSave = () => {
        if (!selectedPartner) return;

        if (selectedPartner.id) {
            setPartners(prev => prev.map(p =>
                p.id === selectedPartner.id ? selectedPartner : p
            ));
        } else {
            const newPartner = {
                ...selectedPartner,
                id: Date.now().toString(),
                api_key_prefix: selectedPartner.name.toLowerCase().replace(/\s+/g, '_').slice(0, 5) + '_live_',
            };
            setPartners(prev => [...prev, newPartner]);
        }
        setShowForm(false);
    };

    const handleSuspend = (partner: Partner) => {
        if (confirm(`Suspend partner "${partner.name}"? This will disable their API access.`)) {
            setPartners(prev => prev.map(p =>
                p.id === partner.id ? { ...p, status: 'suspended' as const } : p
            ));
        }
    };

    const handleActivate = (partner: Partner) => {
        setPartners(prev => prev.map(p =>
            p.id === partner.id ? { ...p, status: 'active' as const } : p
        ));
    };

    const getStatusBadge = (status: Partner['status']) => {
        const styles = {
            active: 'bg-green-500/20 text-green-400 border-green-500/30',
            pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
            suspended: 'bg-red-500/20 text-red-400 border-red-500/30',
        };
        return (
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${styles[status]}`}>
                {status.toUpperCase()}
            </span>
        );
    };

    return (
        <div className="min-h-screen bg-slate-900 text-white">
            {/* Header */}
            <div className="bg-slate-800/50 border-b border-slate-700 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl font-bold">Partner Management</h1>
                            <p className="text-slate-400 text-sm">Embedded Finance SDK / LaaS Administration</p>
                        </div>
                        <button
                            onClick={handleCreate}
                            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                        >
                            <span>+</span> New Partner
                        </button>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 py-6">
                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold">{partners.length}</div>
                        <div className="text-slate-400 text-sm">Total Partners</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold text-green-400">
                            {partners.filter(p => p.status === 'active').length}
                        </div>
                        <div className="text-slate-400 text-sm">Active</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold text-blue-400">
                            {totalRequests.toLocaleString()}
                        </div>
                        <div className="text-slate-400 text-sm">Total Requests</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold">
                            {partners.reduce((sum, p) => sum + p.allowed_programs.length, 0)}
                        </div>
                        <div className="text-slate-400 text-sm">Program Links</div>
                    </div>
                </div>

                {/* Filters */}
                <div className="flex gap-2 mb-6 bg-slate-800 p-1 rounded-lg w-fit">
                    {(['all', 'active', 'pending', 'suspended'] as const).map(status => (
                        <button
                            key={status}
                            onClick={() => setFilter(status)}
                            className={`px-4 py-2 rounded-md font-medium transition-colors ${filter === status
                                    ? 'bg-blue-600 text-white'
                                    : 'text-slate-400 hover:text-white'
                                }`}
                        >
                            {status.charAt(0).toUpperCase() + status.slice(1)}
                        </button>
                    ))}
                </div>

                {/* Partners List */}
                <div className="space-y-4">
                    {filteredPartners.map(partner => (
                        <div
                            key={partner.id}
                            className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden"
                        >
                            <div className="p-4 flex items-start justify-between">
                                <div className="flex items-start gap-4">
                                    {/* Logo / Avatar */}
                                    <div
                                        className="w-12 h-12 rounded-lg flex items-center justify-center text-xl font-bold"
                                        style={{
                                            backgroundColor: partner.branding.primary_color || '#3b82f6',
                                        }}
                                    >
                                        {partner.name.charAt(0)}
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <h3 className="font-semibold text-lg">{partner.name}</h3>
                                            {getStatusBadge(partner.status)}
                                        </div>
                                        <p className="text-slate-400 text-sm mt-1">
                                            API Key: <code className="bg-slate-900 px-1 rounded">{partner.api_key_prefix}***</code>
                                        </p>
                                        <div className="flex gap-4 mt-2 text-sm text-slate-500">
                                            <span>{partner.request_count.toLocaleString()} requests</span>
                                            <span>|</span>
                                            <span>{partner.allowed_programs.length} programs</span>
                                            <span>|</span>
                                            <span>Last active: {new Date(partner.last_active).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => handleEdit(partner)}
                                        className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
                                        title="Edit"
                                    >
                                        ✏️
                                    </button>
                                    <button
                                        onClick={() => { setSelectedPartner(partner); setShowAuditLog(true); }}
                                        className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
                                        title="Audit Log"
                                    >
                                        📜
                                    </button>
                                    {partner.status === 'active' && (
                                        <button
                                            onClick={() => handleSuspend(partner)}
                                            className="p-2 bg-red-600/20 hover:bg-red-600/40 text-red-400 rounded-lg transition-colors"
                                            title="Suspend"
                                        >
                                            ⏸️
                                        </button>
                                    )}
                                    {(partner.status === 'pending' || partner.status === 'suspended') && (
                                        <button
                                            onClick={() => handleActivate(partner)}
                                            className="p-2 bg-green-600/20 hover:bg-green-600/40 text-green-400 rounded-lg transition-colors"
                                            title="Activate"
                                        >
                                            ▶️
                                        </button>
                                    )}
                                </div>
                            </div>

                            {/* Allowed Programs */}
                            <div className="px-4 pb-4">
                                <div className="text-xs text-slate-500 mb-2">Allowed Programs:</div>
                                <div className="flex flex-wrap gap-2">
                                    {partner.allowed_programs.map(progId => {
                                        const prog = MOCK_PROGRAMS.find(p => p.id === progId);
                                        return (
                                            <span key={progId} className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                                                {prog?.name || progId}
                                            </span>
                                        );
                                    })}
                                    {partner.allowed_programs.length === 0 && (
                                        <span className="text-xs text-slate-500 italic">No programs assigned</span>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {filteredPartners.length === 0 && (
                    <div className="text-center py-12 text-slate-500">
                        <div className="text-4xl mb-4">🤝</div>
                        <p>No partners found matching your filter.</p>
                    </div>
                )}
            </div>

            {/* Edit Form Modal */}
            {showForm && selectedPartner && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-800 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div className="sticky top-0 bg-slate-800 p-4 border-b border-slate-700 flex items-center justify-between">
                            <h2 className="text-xl font-semibold">
                                {selectedPartner.id ? 'Edit Partner' : 'Create Partner'}
                            </h2>
                            <button onClick={() => setShowForm(false)} className="p-2 hover:bg-slate-700 rounded-lg">
                                ✕
                            </button>
                        </div>

                        <div className="p-4 space-y-4">
                            {/* Name */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Partner Name</label>
                                <input
                                    type="text"
                                    value={selectedPartner.name}
                                    onChange={(e) => setSelectedPartner({ ...selectedPartner, name: e.target.value })}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2"
                                    placeholder="e.g., FinanceHub Inc."
                                />
                            </div>

                            {/* Allowed Programs */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Allowed Programs</label>
                                <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 grid grid-cols-2 gap-2">
                                    {MOCK_PROGRAMS.map(prog => (
                                        <label key={prog.id} className="flex items-center gap-2 cursor-pointer">
                                            <input
                                                type="checkbox"
                                                checked={selectedPartner.allowed_programs.includes(prog.id)}
                                                onChange={(e) => {
                                                    const updated = e.target.checked
                                                        ? [...selectedPartner.allowed_programs, prog.id]
                                                        : selectedPartner.allowed_programs.filter(id => id !== prog.id);
                                                    setSelectedPartner({ ...selectedPartner, allowed_programs: updated });
                                                }}
                                                className="w-4 h-4 rounded"
                                            />
                                            <span className="text-sm">{prog.name}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            {/* Branding */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Branding</label>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-xs text-slate-400 mb-1">Primary Color</label>
                                        <div className="flex items-center gap-2">
                                            <input
                                                type="color"
                                                value={selectedPartner.branding.primary_color || '#3b82f6'}
                                                onChange={(e) => setSelectedPartner({
                                                    ...selectedPartner,
                                                    branding: { ...selectedPartner.branding, primary_color: e.target.value }
                                                })}
                                                className="w-10 h-10 rounded cursor-pointer"
                                            />
                                            <input
                                                type="text"
                                                value={selectedPartner.branding.primary_color || ''}
                                                onChange={(e) => setSelectedPartner({
                                                    ...selectedPartner,
                                                    branding: { ...selectedPartner.branding, primary_color: e.target.value }
                                                })}
                                                placeholder="#3b82f6"
                                                className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm font-mono"
                                            />
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-xs text-slate-400 mb-1">Logo URL</label>
                                        <input
                                            type="text"
                                            value={selectedPartner.branding.logo_url || ''}
                                            onChange={(e) => setSelectedPartner({
                                                ...selectedPartner,
                                                branding: { ...selectedPartner.branding, logo_url: e.target.value }
                                            })}
                                            placeholder="https://..."
                                            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Callbacks */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Callback URLs</label>
                                <div className="space-y-2">
                                    <div>
                                        <label className="block text-xs text-slate-400 mb-1">Webhook URL</label>
                                        <input
                                            type="text"
                                            value={selectedPartner.callback_urls.webhook || ''}
                                            onChange={(e) => setSelectedPartner({
                                                ...selectedPartner,
                                                callback_urls: { ...selectedPartner.callback_urls, webhook: e.target.value }
                                            })}
                                            placeholder="https://api.partner.com/webhooks/goatcrd"
                                            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs text-slate-400 mb-1">Redirect URL</label>
                                        <input
                                            type="text"
                                            value={selectedPartner.callback_urls.redirect || ''}
                                            onChange={(e) => setSelectedPartner({
                                                ...selectedPartner,
                                                callback_urls: { ...selectedPartner.callback_urls, redirect: e.target.value }
                                            })}
                                            placeholder="https://app.partner.com/results"
                                            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="sticky bottom-0 bg-slate-800 p-4 border-t border-slate-700 flex justify-end gap-3">
                            <button onClick={() => setShowForm(false)} className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg">
                                Cancel
                            </button>
                            <button onClick={handleSave} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium">
                                {selectedPartner.id ? 'Save Changes' : 'Create Partner'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Audit Log Modal */}
            {showAuditLog && selectedPartner && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-800 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div className="sticky top-0 bg-slate-800 p-4 border-b border-slate-700 flex items-center justify-between">
                            <div>
                                <h2 className="text-xl font-semibold">Audit Log</h2>
                                <p className="text-slate-400 text-sm">{selectedPartner.name}</p>
                            </div>
                            <button onClick={() => setShowAuditLog(false)} className="p-2 hover:bg-slate-700 rounded-lg">
                                ✕
                            </button>
                        </div>

                        <div className="divide-y divide-slate-700">
                            {MOCK_AUDIT_LOG.filter(l => l.partner_id === selectedPartner.id).map(entry => (
                                <div key={entry.id} className="p-4 flex items-center justify-between">
                                    <div>
                                        <div className="font-medium">{entry.action}</div>
                                        <div className="text-sm text-slate-400 font-mono">{entry.endpoint}</div>
                                    </div>
                                    <div className="text-right">
                                        <div className={`text-sm font-mono ${entry.status_code < 400 ? 'text-green-400' : 'text-red-400'}`}>
                                            {entry.status_code}
                                        </div>
                                        <div className="text-xs text-slate-500">
                                            {new Date(entry.timestamp).toLocaleString()}
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {MOCK_AUDIT_LOG.filter(l => l.partner_id === selectedPartner.id).length === 0 && (
                                <div className="p-8 text-center text-slate-500">
                                    No audit log entries found.
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
