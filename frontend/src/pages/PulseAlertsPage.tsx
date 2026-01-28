import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const API_URL = '/api/v1';

interface PulseAlert {
    id: string;
    event_type: string;
    summary: string;
    impact: string;
    detected_at: string;
    suggested_action: string | null;
    scenario_refresh_available: boolean;
}

interface PulseSubscription {
    id: string;
    frequency: string;
    active: boolean;
    created_at: string;
}

export function PulseAlertsPage() {
    const { accessToken } = useAuthStore();
    const [alerts, setAlerts] = useState<PulseAlert[]>([]);
    const [subscription, setSubscription] = useState<PulseSubscription | null>(null);
    const [loading, setLoading] = useState(true);
    const [frequency, setFrequency] = useState<string>('daily');

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            // Fetch alerts
            const alertsResponse = await fetch(`${API_URL}/pulse/alerts`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });
            if (alertsResponse.ok) {
                const alertsData = await alertsResponse.json();
                setAlerts(alertsData.alerts || []);
            }

            // Fetch subscription status
            const subResponse = await fetch(`${API_URL}/pulse/subscription`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });
            if (subResponse.ok) {
                const subData = await subResponse.json();
                setSubscription(subData);
                if (subData?.frequency) {
                    setFrequency(subData.frequency);
                }
            }
        } catch (error) {
            console.error('Failed to fetch pulse data:', error);
        } finally {
            setLoading(false);
        }
    };

    const toggleMonitoring = async () => {
        try {
            if (subscription?.active) {
                // Disable
                await fetch(`${API_URL}/pulse/subscription`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                setSubscription(null);
            } else {
                // Enable
                const response = await fetch(`${API_URL}/pulse/subscription`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ frequency })
                });
                if (response.ok) {
                    const data = await response.json();
                    setSubscription(data);
                }
            }
        } catch (error) {
            console.error('Failed to toggle monitoring:', error);
        }
    };

    const updateFrequency = async (newFrequency: string) => {
        setFrequency(newFrequency);
        if (subscription?.active) {
            try {
                await fetch(`${API_URL}/pulse/subscription`, {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ frequency: newFrequency })
                });
            } catch (error) {
                console.error('Failed to update frequency:', error);
            }
        }
    };

    const refreshScenarios = async (alertId: string) => {
        // Would trigger scenario regeneration
        console.log('Refreshing scenarios for alert:', alertId);
    };

    const getEventIcon = (eventType: string) => {
        switch (eventType) {
            case 'new_inquiry': return '🔍';
            case 'balance_change': return '💰';
            case 'new_account': return '📄';
            case 'payment_reported': return '✅';
            case 'delinquency': return '⚠️';
            default: return '📊';
        }
    };

    const getEventColor = (eventType: string) => {
        switch (eventType) {
            case 'payment_reported': return 'border-green-500/30 bg-green-500/10';
            case 'delinquency': return 'border-red-500/30 bg-red-500/10';
            case 'balance_change': return 'border-blue-500/30 bg-blue-500/10';
            default: return 'border-purple-500/30 bg-purple-500/10';
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
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
                        <span className="text-4xl">💓</span>
                        Credit Pulse
                    </h1>
                    <p className="text-white/60 mt-2">
                        Real-time monitoring of your credit profile changes
                    </p>
                </div>
                <Link to="/dashboard" className="btn-secondary">
                    ← Back to Dashboard
                </Link>
            </div>

            {/* Monitoring Control */}
            <div className="glass rounded-xl p-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-semibold text-white">Monitoring Status</h2>
                        <p className="text-white/60 mt-1">
                            {subscription?.active
                                ? `Active • Checking ${subscription.frequency}`
                                : 'Enable monitoring to receive proactive alerts'}
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        <select
                            value={frequency}
                            onChange={(e) => updateFrequency(e.target.value)}
                            className="bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white"
                            disabled={!subscription?.active}
                        >
                            <option value="realtime">Real-time</option>
                            <option value="daily">Daily</option>
                            <option value="weekly">Weekly</option>
                        </select>
                        <button
                            onClick={toggleMonitoring}
                            className={`px-6 py-2 rounded-lg font-medium transition-colors ${subscription?.active
                                ? 'bg-red-500/20 text-red-300 hover:bg-red-500/30'
                                : 'bg-green-500/20 text-green-300 hover:bg-green-500/30'
                                }`}
                        >
                            {subscription?.active ? 'Disable Monitoring' : 'Enable Monitoring'}
                        </button>
                    </div>
                </div>

                {/* Status Indicator */}
                <div className="mt-4 flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${subscription?.active ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
                        }`} />
                    <span className={subscription?.active ? 'text-green-300' : 'text-white/40'}>
                        {subscription?.active ? 'Monitoring Active' : 'Monitoring Disabled'}
                    </span>
                </div>
            </div>

            {/* Alerts Timeline */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-6">Recent Alerts</h2>

                {alerts.length === 0 ? (
                    <div className="text-center py-12">
                        <div className="text-5xl mb-4">🔔</div>
                        <p className="text-white/60 text-lg">No alerts yet</p>
                        <p className="text-white/40 text-sm mt-2">
                            {subscription?.active
                                ? "We'll notify you when we detect changes to your credit profile"
                                : 'Enable monitoring to start receiving alerts'}
                        </p>
                    </div>
                ) : (
                    <div className="relative">
                        {/* Timeline line */}
                        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-white/10" />

                        <div className="space-y-6">
                            {alerts.map((alert) => (
                                <div
                                    key={alert.id}
                                    className={`relative pl-16 ${getEventColor(alert.event_type)} border rounded-lg p-4`}
                                >
                                    {/* Timeline dot */}
                                    <div className="absolute left-4 w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-xs">
                                        {getEventIcon(alert.event_type)}
                                    </div>

                                    <div className="flex items-start justify-between">
                                        <div>
                                            <h3 className="text-white font-medium">{alert.summary}</h3>
                                            <p className="text-white/70 mt-1">{alert.impact}</p>
                                            {alert.suggested_action && (
                                                <p className="text-purple-300 text-sm mt-2">
                                                    💡 {alert.suggested_action}
                                                </p>
                                            )}
                                        </div>
                                        <div className="text-right flex-shrink-0 ml-4">
                                            <p className="text-white/40 text-sm">
                                                {formatDate(alert.detected_at)}
                                            </p>
                                            {alert.scenario_refresh_available && (
                                                <button
                                                    onClick={() => refreshScenarios(alert.id)}
                                                    className="mt-2 text-purple-400 hover:text-purple-300 text-sm"
                                                >
                                                    Refresh Scenarios →
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* What We Monitor */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">What We Monitor</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[
                        { icon: '🔍', title: 'Hard Inquiries', desc: 'New credit applications' },
                        { icon: '💳', title: 'Balance Changes', desc: 'Significant credit utilization shifts' },
                        { icon: '📄', title: 'New Accounts', desc: 'Recently opened credit accounts' },
                        { icon: '✅', title: 'Payments', desc: 'On-time payment reporting' },
                        { icon: '⚠️', title: 'Delinquencies', desc: 'Late payment alerts' },
                        { icon: '📊', title: 'Score Changes', desc: 'Credit score movements' },
                    ].map((item, i) => (
                        <div key={i} className="bg-white/5 rounded-lg p-4 border border-white/10">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl">{item.icon}</span>
                                <div>
                                    <h3 className="text-white font-medium">{item.title}</h3>
                                    <p className="text-white/50 text-sm">{item.desc}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Privacy Note */}
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                <div className="flex items-start gap-3">
                    <span className="text-xl">🔒</span>
                    <div>
                        <h3 className="text-blue-300 font-medium">Your Privacy Matters</h3>
                        <p className="text-white/60 text-sm mt-1">
                            Credit Pulse is opt-in only. You can disable monitoring at any time,
                            and we'll stop all data collection within 24 hours. Your data is never
                            shared without explicit consent.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default PulseAlertsPage;
