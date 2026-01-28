import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface MonitoringMetric {
    name: string;
    current: number;
    baseline: number;
    trend: 'up' | 'down' | 'stable';
    threshold: number;
    status: 'healthy' | 'warning' | 'critical';
}

interface ServiceHealth {
    service: string;
    status: 'healthy' | 'degraded' | 'down';
    latency_p99: number;
    error_rate: number;
    last_deployment: string;
}

interface Alert {
    id: string;
    severity: 'info' | 'warning' | 'critical';
    message: string;
    timestamp: string;
    acknowledged: boolean;
}

const MOCK_METRICS: MonitoringMetric[] = [
    { name: 'Approval Rate', current: 0.67, baseline: 0.65, trend: 'up', threshold: 0.60, status: 'healthy' },
    { name: 'Avg Decision Time', current: 1.2, baseline: 1.5, trend: 'down', threshold: 2.0, status: 'healthy' },
    { name: 'DI Ratio (Age)', current: 0.82, baseline: 0.85, trend: 'down', threshold: 0.80, status: 'warning' },
    { name: 'DI Ratio (Gender)', current: 0.91, baseline: 0.90, trend: 'up', threshold: 0.80, status: 'healthy' },
    { name: 'Error Rate', current: 0.02, baseline: 0.015, trend: 'up', threshold: 0.05, status: 'healthy' },
    { name: 'Human Review %', current: 0.08, baseline: 0.10, trend: 'down', threshold: 0.15, status: 'healthy' },
];

const MOCK_SERVICES: ServiceHealth[] = [
    { service: 'Decision API', status: 'healthy', latency_p99: 145, error_rate: 0.01, last_deployment: '2 hours ago' },
    { service: 'Rules Engine', status: 'healthy', latency_p99: 52, error_rate: 0.0, last_deployment: '1 day ago' },
    { service: 'Fairness Monitor', status: 'healthy', latency_p99: 230, error_rate: 0.02, last_deployment: '3 days ago' },
    { service: 'Audit Logger', status: 'degraded', latency_p99: 890, error_rate: 0.05, last_deployment: '5 hours ago' },
];

const MOCK_ALERTS: Alert[] = [
    { id: 'a1', severity: 'warning', message: 'DI Ratio for age approaching threshold (82%)', timestamp: new Date(Date.now() - 1800000).toISOString(), acknowledged: false },
    { id: 'a2', severity: 'info', message: 'New deployment completed: Decision API v2.3.1', timestamp: new Date(Date.now() - 7200000).toISOString(), acknowledged: true },
    { id: 'a3', severity: 'critical', message: 'Audit Logger latency spike detected (>800ms p99)', timestamp: new Date(Date.now() - 3600000).toISOString(), acknowledged: false },
];

export default function PostDeployMonitoring() {
    const [metrics] = useState<MonitoringMetric[]>(MOCK_METRICS);
    const [services] = useState<ServiceHealth[]>(MOCK_SERVICES);
    const [alerts, setAlerts] = useState<Alert[]>(MOCK_ALERTS);
    const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('24h');
    const [lastUpdated, setLastUpdated] = useState(new Date());

    useEffect(() => {
        const interval = setInterval(() => setLastUpdated(new Date()), 30000);
        return () => clearInterval(interval);
    }, []);

    const acknowledgeAlert = (id: string) => {
        setAlerts(prev => prev.map(a => a.id === id ? { ...a, acknowledged: true } : a));
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'healthy': return 'bg-green-500';
            case 'warning': case 'degraded': return 'bg-yellow-500';
            case 'critical': case 'down': return 'bg-red-500';
            default: return 'bg-gray-500';
        }
    };

    const getTrendIcon = (trend: string) => {
        switch (trend) {
            case 'up': return '↑';
            case 'down': return '↓';
            default: return '→';
        }
    };

    const getSeverityStyle = (severity: string) => {
        switch (severity) {
            case 'critical': return 'border-red-500 bg-red-500/10';
            case 'warning': return 'border-yellow-500 bg-yellow-500/10';
            default: return 'border-blue-500 bg-blue-500/10';
        }
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                        <span className="text-4xl">📡</span>
                        Post-Deploy Monitoring
                    </h1>
                    <p className="text-white/60 mt-2">
                        Real-time production health and fairness drift detection
                    </p>
                </div>
                <div className="flex items-center gap-4">
                    <span className="text-white/40 text-sm">
                        Last updated: {lastUpdated.toLocaleTimeString()}
                    </span>
                    <Link to="/admin/fairness" className="btn-secondary">
                        ← Back to Dashboard
                    </Link>
                </div>
            </div>

            {/* Time Range Selector */}
            <div className="flex gap-2">
                {(['1h', '6h', '24h', '7d'] as const).map(range => (
                    <button
                        key={range}
                        onClick={() => setTimeRange(range)}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${timeRange === range
                                ? 'bg-purple-500 text-white'
                                : 'bg-white/10 text-white/60 hover:text-white'
                            }`}
                    >
                        {range}
                    </button>
                ))}
            </div>

            {/* Alerts Panel */}
            {alerts.filter(a => !a.acknowledged).length > 0 && (
                <div className="space-y-3">
                    <h2 className="text-lg font-semibold text-white">Active Alerts</h2>
                    {alerts.filter(a => !a.acknowledged).map(alert => (
                        <div
                            key={alert.id}
                            className={`border-l-4 rounded-lg p-4 flex items-center justify-between ${getSeverityStyle(alert.severity)}`}
                        >
                            <div>
                                <span className={`text-xs font-medium uppercase ${alert.severity === 'critical' ? 'text-red-400' :
                                        alert.severity === 'warning' ? 'text-yellow-400' : 'text-blue-400'
                                    }`}>
                                    {alert.severity}
                                </span>
                                <p className="text-white mt-1">{alert.message}</p>
                                <p className="text-white/50 text-sm mt-1">
                                    {new Date(alert.timestamp).toLocaleString()}
                                </p>
                            </div>
                            <button
                                onClick={() => acknowledgeAlert(alert.id)}
                                className="px-3 py-1 bg-white/10 rounded text-white/60 hover:text-white text-sm"
                            >
                                Acknowledge
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Metrics Panel */}
                <div className="glass rounded-xl p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">Key Metrics</h2>
                    <div className="space-y-4">
                        {metrics.map(metric => (
                            <div key={metric.name} className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className={`w-2 h-2 rounded-full ${getStatusColor(metric.status)}`} />
                                    <span className="text-white">{metric.name}</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className={`text-lg font-medium ${metric.status === 'healthy' ? 'text-white' :
                                            metric.status === 'warning' ? 'text-yellow-400' : 'text-red-400'
                                        }`}>
                                        {metric.name.includes('Rate') || metric.name.includes('%') || metric.name.includes('DI')
                                            ? `${(metric.current * 100).toFixed(1)}%`
                                            : metric.name.includes('Time') ? `${metric.current}s` : metric.current
                                        }
                                    </span>
                                    <span className={`text-sm ${metric.trend === 'up' ? 'text-green-400' :
                                            metric.trend === 'down' ? 'text-red-400' : 'text-white/40'
                                        }`}>
                                        {getTrendIcon(metric.trend)}
                                        {Math.abs(((metric.current - metric.baseline) / metric.baseline) * 100).toFixed(1)}%
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Service Health Panel */}
                <div className="glass rounded-xl p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">Service Health</h2>
                    <div className="space-y-4">
                        {services.map(service => (
                            <div key={service.service} className="bg-white/5 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-white font-medium">{service.service}</span>
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${service.status === 'healthy' ? 'bg-green-500/20 text-green-400' :
                                            service.status === 'degraded' ? 'bg-yellow-500/20 text-yellow-400' :
                                                'bg-red-500/20 text-red-400'
                                        }`}>
                                        {service.status.toUpperCase()}
                                    </span>
                                </div>
                                <div className="grid grid-cols-3 gap-4 text-sm">
                                    <div>
                                        <span className="text-white/50">Latency p99</span>
                                        <span className={`block font-medium ${service.latency_p99 < 200 ? 'text-green-400' :
                                                service.latency_p99 < 500 ? 'text-yellow-400' : 'text-red-400'
                                            }`}>
                                            {service.latency_p99}ms
                                        </span>
                                    </div>
                                    <div>
                                        <span className="text-white/50">Error Rate</span>
                                        <span className={`block font-medium ${service.error_rate < 0.02 ? 'text-green-400' :
                                                service.error_rate < 0.05 ? 'text-yellow-400' : 'text-red-400'
                                            }`}>
                                            {(service.error_rate * 100).toFixed(2)}%
                                        </span>
                                    </div>
                                    <div>
                                        <span className="text-white/50">Last Deploy</span>
                                        <span className="block text-white">{service.last_deployment}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Fairness Drift Visualization */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Fairness Metrics Over Time</h2>
                <div className="h-48 bg-white/5 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                        <p className="text-white/60">📈 Trend visualization</p>
                        <p className="text-white/40 text-sm mt-2">
                            Connect to Prometheus/Grafana for live charts
                        </p>
                    </div>
                </div>
                <div className="flex justify-center gap-6 mt-4">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-green-500" />
                        <span className="text-white/60 text-sm">DI Ratio (Gender)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-yellow-500" />
                        <span className="text-white/60 text-sm">DI Ratio (Age)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-blue-500" />
                        <span className="text-white/60 text-sm">Approval Rate</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
