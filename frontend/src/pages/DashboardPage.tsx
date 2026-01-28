import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { CoachWidget } from '../components/CoachWidget';

const API_URL = '/api/v1';

interface Case {
    id: string;
    case_type: string;
    status: string;
    created_at: string;
    updated_at: string;
}

export function DashboardPage() {
    const { accessToken, user } = useAuthStore();
    const [cases, setCases] = useState<Case[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isCreating, setIsCreating] = useState(false);

    useEffect(() => {
        fetchCases();
    }, [accessToken]);

    const fetchCases = async () => {
        if (!accessToken) return;

        setIsLoading(true);
        try {
            const response = await fetch(`${API_URL}/cases`, {
                headers: { 'Authorization': `Bearer ${accessToken}` },
            });
            if (response.ok) {
                const data = await response.json();
                setCases(data);
            }
        } catch (error) {
            console.error('Failed to fetch cases:', error);
        }
        setIsLoading(false);
    };

    const createCase = async () => {
        if (!accessToken) return;

        setIsCreating(true);
        try {
            const response = await fetch(`${API_URL}/cases`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: JSON.stringify({ case_type: 'personal_loan' }),
            });

            if (response.ok) {
                const newCase = await response.json();
                setCases([newCase, ...cases]);
            }
        } catch (error) {
            console.error('Failed to create case:', error);
        }
        setIsCreating(false);
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'draft': return 'bg-gray-500';
            case 'intake_in_progress': return 'bg-yellow-500';
            case 'intake_complete': return 'bg-blue-500';
            case 'scenarios_ready': return 'bg-green-500';
            default: return 'bg-gray-500';
        }
    };

    const getStatusLabel = (status: string) => {
        switch (status) {
            case 'draft': return 'Draft';
            case 'intake_in_progress': return 'Intake In Progress';
            case 'intake_complete': return 'Intake Complete';
            case 'scenarios_ready': return 'Ready for Review';
            default: return status;
        }
    };

    return (
        <div className="py-8">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold">
                        Welcome back{user?.first_name ? `, ${user.first_name}` : ''}!
                    </h1>
                    <p className="text-white/70">Manage your credit scenarios</p>
                </div>
                <button
                    onClick={createCase}
                    disabled={isCreating}
                    className="btn-primary"
                >
                    {isCreating ? 'Creating...' : '+ New Application'}
                </button>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <Link to="/alternative-data" className="glass-card p-4 text-center hover:border-purple-500/30 transition-all">
                    <div className="text-3xl mb-2">🏦</div>
                    <div className="text-sm font-medium text-white">Connect Bank</div>
                    <div className="text-xs text-white/50">Alternative Data</div>
                </Link>
                <Link to="/pulse-alerts" className="glass-card p-4 text-center hover:border-purple-500/30 transition-all">
                    <div className="text-3xl mb-2">💓</div>
                    <div className="text-sm font-medium text-white">Credit Pulse</div>
                    <div className="text-xs text-white/50">Active Monitoring</div>
                </Link>
                <Link to="/my-data" className="glass-card p-4 text-center hover:border-purple-500/30 transition-all">
                    <div className="text-3xl mb-2">🔐</div>
                    <div className="text-sm font-medium text-white">My Data</div>
                    <div className="text-xs text-white/50">Privacy Controls</div>
                </Link>
                <Link to="/what-if" className="glass-card p-4 text-center hover:border-purple-500/30 transition-all">
                    <div className="text-3xl mb-2">🔮</div>
                    <div className="text-sm font-medium text-white">What-If</div>
                    <div className="text-xs text-white/50">Scenario Simulator</div>
                </Link>
            </div>

            {/* Coach Widget */}
            <div className="mb-8">
                <CoachWidget />
            </div>

            {/* Cases Grid */}
            {isLoading ? (
                <div className="glass-card p-12 text-center">
                    <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
                    <p className="text-white/60">Loading your cases...</p>
                </div>
            ) : cases.length === 0 ? (
                <div className="glass-card p-12 text-center">
                    <div className="text-6xl mb-4">📋</div>
                    <h2 className="text-xl font-semibold mb-2">No applications yet</h2>
                    <p className="text-white/60 mb-6">
                        Start your first credit scenario to see personalized options
                    </p>
                    <button onClick={createCase} className="btn-primary">
                        Start Your First Application
                    </button>
                </div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {cases.map((caseItem) => (
                        <div key={caseItem.id} className="glass-card p-6 hover:border-primary-500/30 transition-all">
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <span className="text-sm text-white/60">
                                        {caseItem.case_type.replace('_', ' ').toUpperCase()}
                                    </span>
                                    <h3 className="font-semibold">
                                        Case #{caseItem.id.slice(0, 8)}
                                    </h3>
                                </div>
                                <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(caseItem.status)}`}>
                                    {getStatusLabel(caseItem.status)}
                                </span>
                            </div>

                            <p className="text-sm text-white/60 mb-4">
                                Created {new Date(caseItem.created_at).toLocaleDateString()}
                            </p>

                            <div className="flex gap-2">
                                {caseItem.status === 'draft' || caseItem.status === 'intake_in_progress' ? (
                                    <Link
                                        to={`/intake/${caseItem.id}`}
                                        className="btn-primary text-sm flex-1 text-center"
                                    >
                                        Continue Intake
                                    </Link>
                                ) : (
                                    <Link
                                        to="/scenarios"
                                        className="btn-primary text-sm flex-1 text-center"
                                    >
                                        View Scenarios
                                    </Link>
                                )}
                                <Link
                                    to="/audit-viewer"
                                    className="bg-white/10 hover:bg-white/20 text-white/80 text-sm px-3 py-2 rounded-lg"
                                    title="View Audit Trail"
                                >
                                    📋
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Quick Stats */}
            {cases.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
                    <div className="glass-card p-4 text-center">
                        <div className="text-3xl font-bold text-primary-400">{cases.length}</div>
                        <div className="text-sm text-white/60">Total Cases</div>
                    </div>
                    <div className="glass-card p-4 text-center">
                        <div className="text-3xl font-bold text-yellow-400">
                            {cases.filter(c => c.status === 'intake_in_progress').length}
                        </div>
                        <div className="text-sm text-white/60">In Progress</div>
                    </div>
                    <div className="glass-card p-4 text-center">
                        <div className="text-3xl font-bold text-green-400">
                            {cases.filter(c => c.status === 'scenarios_ready').length}
                        </div>
                        <div className="text-sm text-white/60">Ready</div>
                    </div>
                    <div className="glass-card p-4 text-center">
                        <div className="text-3xl font-bold text-blue-400">
                            {cases.filter(c => c.status === 'intake_complete').length}
                        </div>
                        <div className="text-sm text-white/60">Complete</div>
                    </div>
                </div>
            )}
        </div>
    );
}

