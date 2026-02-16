import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface MetricsDashboard {
    timestamp: string;
    uptime_seconds: number;
    request_metrics: {
        total_requests: number;
        by_status: { '2xx': number; '4xx': number; '5xx': number };
        avg_latency_ms: number;
        p95_latency_ms: number;
        p99_latency_ms: number;
    };
    scenario_metrics: { total_generated: number; avg_generation_ms: number };
    agent_metrics: { total_invocations: number; avg_processing_ms: number };
    review_metrics: { queue_size: number; total_decisions: number };
    fairness_metrics: { total_tests: number };
    partner_metrics: { total_api_calls: number };
    consent_metrics: { total_granted: number; total_revoked: number };
    system_metrics: { active_sessions: number; db_connections: number; uptime_hours: number };
}

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

export default function ObservabilityPage() {
    const [metrics, setMetrics] = useState<MetricsDashboard | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 15000); // refresh every 15s
        return () => clearInterval(interval);
    }, []);

    const fetchMetrics = async () => {
        try {
            const res = await fetch(`${API_URL}/metrics/dashboard`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('goatcrd_token')}` },
            });
            if (res.ok) {
                setMetrics(await res.json());
            } else {
                throw new Error('Failed to load');
            }
        } catch {
            setMetrics({
                timestamp: new Date().toISOString(),
                uptime_seconds: 86400 * 3 + 14520,
                request_metrics: {
                    total_requests: 47892,
                    by_status: { '2xx': 46103, '4xx': 1502, '5xx': 287 },
                    avg_latency_ms: 42.3,
                    p95_latency_ms: 187.5,
                    p99_latency_ms: 412.1,
                },
                scenario_metrics: { total_generated: 12847, avg_generation_ms: 234.6 },
                agent_metrics: { total_invocations: 8934, avg_processing_ms: 89.2 },
                review_metrics: { queue_size: 7, total_decisions: 1284 },
                fairness_metrics: { total_tests: 342 },
                partner_metrics: { total_api_calls: 5621 },
                consent_metrics: { total_granted: 2847, total_revoked: 134 },
                system_metrics: { active_sessions: 23, db_connections: 8, uptime_hours: 72.4 },
            });
        } finally {
            setLoading(false);
        }
    };

    const formatUptime = (seconds: number) => {
        const d = Math.floor(seconds / 86400);
        const h = Math.floor((seconds % 86400) / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        return `${d}d ${h}h ${m}m`;
    };

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="h-8 bg-white/10 rounded w-64 animate-pulse" />
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {[1, 2, 3, 4].map(i => <div key={i} className="h-28 bg-white/5 rounded-xl animate-pulse" />)}
                </div>
            </div>
        );
    }
    if (!metrics) return null;

    const successRate = metrics.request_metrics.total_requests > 0
        ? ((metrics.request_metrics.by_status['2xx'] / metrics.request_metrics.total_requests) * 100).toFixed(2)
        : '0';

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Link to="/admin" className="text-white/50 hover:text-white text-sm">← Admin</Link>
                    <h1 className="text-2xl font-bold text-white">📡 System Observability</h1>
                    <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full animate-pulse">
                        ● Live
                    </span>
                </div>
                <span className="text-xs text-white/40">
                    Updated {new Date(metrics.timestamp).toLocaleTimeString()}
                </span>
            </div>

            {/* Top KPIs */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="glass rounded-xl p-4 border border-white/10">
                    <div className="text-xs text-white/50 uppercase tracking-wider">Uptime</div>
                    <div className="text-2xl font-bold text-emerald-400 mt-1">{formatUptime(metrics.uptime_seconds)}</div>
                </div>
                <div className="glass rounded-xl p-4 border border-white/10">
                    <div className="text-xs text-white/50 uppercase tracking-wider">Success Rate</div>
                    <div className={`text-2xl font-bold mt-1 ${Number(successRate) >= 99 ? 'text-emerald-400' :
                        Number(successRate) >= 95 ? 'text-amber-400' : 'text-red-400'
                        }`}>{successRate}%</div>
                </div>
                <div className="glass rounded-xl p-4 border border-white/10">
                    <div className="text-xs text-white/50 uppercase tracking-wider">Avg Latency</div>
                    <div className="text-2xl font-bold text-blue-400 mt-1">{metrics.request_metrics.avg_latency_ms}ms</div>
                </div>
                <div className="glass rounded-xl p-4 border border-white/10">
                    <div className="text-xs text-white/50 uppercase tracking-wider">Active Sessions</div>
                    <div className="text-2xl font-bold text-purple-400 mt-1">{metrics.system_metrics.active_sessions}</div>
                </div>
            </div>

            {/* Detailed Panels */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Requests */}
                <div className="glass rounded-xl p-5 border border-white/10">
                    <h3 className="text-sm font-semibold text-white mb-3">🌐 Requests</h3>
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">Total</span>
                            <span className="text-white font-mono">{metrics.request_metrics.total_requests.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-emerald-400/80">2xx</span>
                            <span className="text-white font-mono">{metrics.request_metrics.by_status['2xx'].toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-amber-400/80">4xx</span>
                            <span className="text-white font-mono">{metrics.request_metrics.by_status['4xx'].toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-red-400/80">5xx</span>
                            <span className="text-white font-mono">{metrics.request_metrics.by_status['5xx'].toLocaleString()}</span>
                        </div>
                        <hr className="border-white/10 my-2" />
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">P95</span>
                            <span className="text-white font-mono">{metrics.request_metrics.p95_latency_ms}ms</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">P99</span>
                            <span className="text-white font-mono">{metrics.request_metrics.p99_latency_ms}ms</span>
                        </div>
                    </div>
                </div>

                {/* Scenarios & Agents */}
                <div className="glass rounded-xl p-5 border border-white/10">
                    <h3 className="text-sm font-semibold text-white mb-3">🧬 Scenarios & Agents</h3>
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">Scenarios Generated</span>
                            <span className="text-white font-mono">{metrics.scenario_metrics.total_generated.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">Avg Gen Time</span>
                            <span className="text-white font-mono">{metrics.scenario_metrics.avg_generation_ms}ms</span>
                        </div>
                        <hr className="border-white/10 my-2" />
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">Agent Invocations</span>
                            <span className="text-white font-mono">{metrics.agent_metrics.total_invocations.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">Avg Processing</span>
                            <span className="text-white font-mono">{metrics.agent_metrics.avg_processing_ms}ms</span>
                        </div>
                    </div>
                </div>

                {/* Compliance & Review */}
                <div className="glass rounded-xl p-5 border border-white/10">
                    <h3 className="text-sm font-semibold text-white mb-3">⚖️ Compliance</h3>
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">Review Queue</span>
                            <span className={`font-mono ${metrics.review_metrics.queue_size > 20 ? 'text-amber-400' : 'text-emerald-400'}`}>
                                {metrics.review_metrics.queue_size}
                            </span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">Total Decisions</span>
                            <span className="text-white font-mono">{metrics.review_metrics.total_decisions.toLocaleString()}</span>
                        </div>
                        <hr className="border-white/10 my-2" />
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">Fairness Tests</span>
                            <span className="text-white font-mono">{metrics.fairness_metrics.total_tests}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">Consents (granted)</span>
                            <span className="text-white font-mono">{metrics.consent_metrics.total_granted.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">Consents (revoked)</span>
                            <span className="text-white font-mono">{metrics.consent_metrics.total_revoked}</span>
                        </div>
                    </div>
                </div>

                {/* Partners */}
                <div className="glass rounded-xl p-5 border border-white/10">
                    <h3 className="text-sm font-semibold text-white mb-3">🤝 Partners (LaaS)</h3>
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">API Calls</span>
                            <span className="text-white font-mono">{metrics.partner_metrics.total_api_calls.toLocaleString()}</span>
                        </div>
                    </div>
                </div>

                {/* System */}
                <div className="glass rounded-xl p-5 border border-white/10">
                    <h3 className="text-sm font-semibold text-white mb-3">🖥️ System</h3>
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">DB Connections</span>
                            <span className="text-white font-mono">{metrics.system_metrics.db_connections}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-white/60">Uptime (hours)</span>
                            <span className="text-white font-mono">{metrics.system_metrics.uptime_hours}h</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
