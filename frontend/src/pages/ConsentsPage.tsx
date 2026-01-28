import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface Consent {
    id: string;
    purpose: string;
    description: string;
    granted: boolean;
    granted_at?: string;
    revoked_at?: string;
    expires_at?: string;
    source_ids: string[];
    downstream_disabled?: boolean;
    downstream_disabled_at?: string;
    downstream_disable_verified?: boolean;
}

interface ConsentEvent {
    id: string;
    consent_id: string;
    event_type: 'granted' | 'revoked' | 'expired' | 'downstream_verified';
    timestamp: string;
    details?: string;
}

export function ConsentsPage() {
    const [consents, setConsents] = useState<Consent[]>([]);
    const [events, setEvents] = useState<ConsentEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedConsent, setSelectedConsent] = useState<string | null>(null);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        // Mock data
        const mockConsents: Consent[] = [
            {
                id: 'consent-001',
                purpose: 'credit_bureau_pull',
                description: 'Allow credit bureau data pull for eligibility assessment',
                granted: true,
                granted_at: new Date(Date.now() - 7 * 86400000).toISOString(),
                expires_at: new Date(Date.now() + 23 * 86400000).toISOString(),
                source_ids: ['experian', 'equifax']
            },
            {
                id: 'consent-002',
                purpose: 'income_verification',
                description: 'Allow payroll API access for income verification',
                granted: true,
                granted_at: new Date(Date.now() - 5 * 86400000).toISOString(),
                source_ids: ['payroll_provider']
            },
            {
                id: 'consent-003',
                purpose: 'bank_connection',
                description: 'Allow bank account connection via Plaid for cash flow analysis',
                granted: true,
                granted_at: new Date(Date.now() - 3 * 86400000).toISOString(),
                source_ids: ['plaid']
            },
            {
                id: 'consent-004',
                purpose: 'partner_share',
                description: 'Allow sharing scenarios with partner lenders',
                granted: false,
                revoked_at: new Date(Date.now() - 10 * 86400000).toISOString(),
                source_ids: ['partner_api'],
                downstream_disabled: true,
                downstream_disabled_at: new Date(Date.now() - 9 * 86400000).toISOString(),
                downstream_disable_verified: true
            }
        ];

        const mockEvents: ConsentEvent[] = [
            { id: 'evt-001', consent_id: 'consent-004', event_type: 'revoked', timestamp: new Date(Date.now() - 10 * 86400000).toISOString() },
            { id: 'evt-002', consent_id: 'consent-004', event_type: 'downstream_verified', timestamp: new Date(Date.now() - 9 * 86400000).toISOString(), details: 'Partner API confirmed data deletion' },
            { id: 'evt-003', consent_id: 'consent-001', event_type: 'granted', timestamp: new Date(Date.now() - 7 * 86400000).toISOString() }
        ];

        setConsents(mockConsents);
        setEvents(mockEvents);
        setLoading(false);
    };

    const toggleConsent = async (consentId: string) => {
        setConsents(prev =>
            prev.map(c => {
                if (c.id === consentId) {
                    return {
                        ...c,
                        granted: !c.granted,
                        [c.granted ? 'revoked_at' : 'granted_at']: new Date().toISOString()
                    };
                }
                return c;
            })
        );
        // Would call API to update
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    };

    const getDaysUntilExpiry = (expiresAt: string) => {
        const days = Math.ceil((new Date(expiresAt).getTime() - Date.now()) / 86400000);
        return days;
    };

    const getConsentIcon = (purpose: string): string => {
        const icons: Record<string, string> = {
            'credit_bureau_pull': '📊',
            'income_verification': '💰',
            'bank_connection': '🏦',
            'partner_share': '🤝',
            'marketing': '📧',
            'analytics': '📈'
        };
        return icons[purpose] || '📋';
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
                        <span className="text-4xl">🔐</span>
                        Consent Management
                    </h1>
                    <p className="text-white/60 mt-2">
                        Control what data can be accessed and shared
                    </p>
                </div>
                <Link to="/my-data" className="btn-secondary">
                    ← Back
                </Link>
            </div>

            {/* Summary */}
            <div className="grid grid-cols-3 gap-4">
                <div className="glass rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-green-400">{consents.filter(c => c.granted).length}</p>
                    <p className="text-white/50 text-sm">Active Consents</p>
                </div>
                <div className="glass rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-red-400">{consents.filter(c => !c.granted).length}</p>
                    <p className="text-white/50 text-sm">Revoked</p>
                </div>
                <div className="glass rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-yellow-400">
                        {consents.filter(c => c.expires_at && getDaysUntilExpiry(c.expires_at) <= 7).length}
                    </p>
                    <p className="text-white/50 text-sm">Expiring Soon</p>
                </div>
            </div>

            {/* Consent List */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Your Consents</h2>
                <div className="space-y-4">
                    {consents.map(consent => (
                        <div
                            key={consent.id}
                            className={`bg-white/5 rounded-lg p-4 border transition-colors ${selectedConsent === consent.id ? 'border-purple-500' : 'border-white/10'
                                }`}
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex items-start gap-3 flex-1" onClick={() => setSelectedConsent(selectedConsent === consent.id ? null : consent.id)}>
                                    <span className="text-2xl">{getConsentIcon(consent.purpose)}</span>
                                    <div className="flex-1 cursor-pointer">
                                        <h3 className="text-white font-medium capitalize">
                                            {consent.purpose.replace(/_/g, ' ')}
                                        </h3>
                                        <p className="text-white/50 text-sm mt-1">{consent.description}</p>

                                        {/* Status */}
                                        <div className="flex flex-wrap gap-2 mt-3">
                                            <span className={`text-xs px-2 py-0.5 rounded-full ${consent.granted
                                                    ? 'bg-green-500/20 text-green-300'
                                                    : 'bg-red-500/20 text-red-300'
                                                }`}>
                                                {consent.granted ? 'Active' : 'Revoked'}
                                            </span>
                                            {consent.expires_at && consent.granted && (
                                                <span className={`text-xs px-2 py-0.5 rounded-full ${getDaysUntilExpiry(consent.expires_at) <= 7
                                                        ? 'bg-yellow-500/20 text-yellow-300'
                                                        : 'bg-white/10 text-white/50'
                                                    }`}>
                                                    Expires: {formatDate(consent.expires_at)}
                                                </span>
                                            )}
                                            {consent.downstream_disable_verified && (
                                                <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300">
                                                    ✓ Downstream Verified
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {/* Toggle */}
                                <button
                                    onClick={() => toggleConsent(consent.id)}
                                    className={`w-12 h-6 rounded-full relative transition-colors ${consent.granted ? 'bg-green-500' : 'bg-gray-600'
                                        }`}
                                >
                                    <span className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${consent.granted ? 'right-1' : 'left-1'
                                        }`} />
                                </button>
                            </div>

                            {/* Expanded Details */}
                            {selectedConsent === consent.id && (
                                <div className="mt-4 pt-4 border-t border-white/10">
                                    <div className="grid grid-cols-2 gap-4 text-sm">
                                        <div>
                                            <p className="text-white/50">Data Sources</p>
                                            <p className="text-white">{consent.source_ids.join(', ')}</p>
                                        </div>
                                        <div>
                                            <p className="text-white/50">Granted</p>
                                            <p className="text-white">{consent.granted_at ? formatDate(consent.granted_at) : '—'}</p>
                                        </div>
                                        {consent.revoked_at && (
                                            <div>
                                                <p className="text-white/50">Revoked</p>
                                                <p className="text-white">{formatDate(consent.revoked_at)}</p>
                                            </div>
                                        )}
                                    </div>

                                    {/* Event History */}
                                    <div className="mt-4">
                                        <p className="text-white/50 text-sm mb-2">Event History</p>
                                        <div className="space-y-2">
                                            {events
                                                .filter(e => e.consent_id === consent.id)
                                                .map(event => (
                                                    <div key={event.id} className="flex items-center gap-2 text-xs">
                                                        <span className={`w-2 h-2 rounded-full ${event.event_type === 'granted' ? 'bg-green-500' :
                                                                event.event_type === 'revoked' ? 'bg-red-500' :
                                                                    event.event_type === 'downstream_verified' ? 'bg-blue-500' :
                                                                        'bg-yellow-500'
                                                            }`} />
                                                        <span className="text-white/60">{formatDate(event.timestamp)}</span>
                                                        <span className="text-white capitalize">{event.event_type.replace('_', ' ')}</span>
                                                        {event.details && <span className="text-white/40">— {event.details}</span>}
                                                    </div>
                                                ))}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Revoke All */}
            <div className="glass rounded-xl p-6 border border-red-500/20">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                            <span className="text-red-400">⚠️</span>
                            Revoke All Consents
                        </h2>
                        <p className="text-white/60 mt-1">
                            Immediately disable all data access and sharing
                        </p>
                    </div>
                    <button
                        onClick={() => consents.filter(c => c.granted).forEach(c => toggleConsent(c.id))}
                        className="bg-red-500/20 text-red-300 hover:bg-red-500/30 px-6 py-2 rounded-lg transition-colors"
                    >
                        Revoke All
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ConsentsPage;
