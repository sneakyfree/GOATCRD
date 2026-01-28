import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface RetentionCategory {
    id: string;
    name: string;
    description: string;
    data_types: string[];
    current_retention_days: number;
    min_days: number;
    max_days: number;
    records_count: number;
}

interface DeletionRequest {
    id: string;
    status: 'pending' | 'processing' | 'completed' | 'verified';
    requested_at: string;
    completed_at?: string;
    categories: string[];
}

export function RetentionSettingsPage() {
    const [categories, setCategories] = useState<RetentionCategory[]>([]);
    const [deletionRequests, setDeletionRequests] = useState<DeletionRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [deletingAll, setDeletingAll] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        // Mock data
        const mockCategories: RetentionCategory[] = [
            {
                id: 'intake',
                name: 'Intake Data',
                description: 'Personal and financial information from applications',
                data_types: ['Personal Info', 'Income Data', 'Employment'],
                current_retention_days: 365,
                min_days: 30,
                max_days: 730,
                records_count: 47
            },
            {
                id: 'scenarios',
                name: 'Scenario Results',
                description: 'Generated loan scenarios and eligibility data',
                data_types: ['Scenarios', 'Rankings', 'Recommendations'],
                current_retention_days: 180,
                min_days: 30,
                max_days: 365,
                records_count: 12
            },
            {
                id: 'credit',
                name: 'Credit Data',
                description: 'Credit bureau pulls and tradeline information',
                data_types: ['Credit Reports', 'Scores', 'Tradelines'],
                current_retention_days: 365,
                min_days: 90,
                max_days: 730,
                records_count: 3
            },
            {
                id: 'bank',
                name: 'Bank Connection Data',
                description: 'Connected account and transaction data',
                data_types: ['Transactions', 'Balances', 'Cash Flow'],
                current_retention_days: 90,
                min_days: 30,
                max_days: 365,
                records_count: 289
            }
        ];

        const mockDeletionRequests: DeletionRequest[] = [
            {
                id: 'del-001',
                status: 'completed',
                requested_at: new Date(Date.now() - 30 * 86400000).toISOString(),
                completed_at: new Date(Date.now() - 28 * 86400000).toISOString(),
                categories: ['scenarios']
            }
        ];

        setCategories(mockCategories);
        setDeletionRequests(mockDeletionRequests);
        setLoading(false);
    };

    const updateRetention = async (categoryId: string, days: number) => {
        setCategories(prev =>
            prev.map(c => c.id === categoryId ? { ...c, current_retention_days: days } : c)
        );
        // Would call API to persist
    };

    const requestDeletion = async (categoryIds: string[]) => {
        const newRequest: DeletionRequest = {
            id: `del-${Date.now()}`,
            status: 'pending',
            requested_at: new Date().toISOString(),
            categories: categoryIds
        };
        setDeletionRequests(prev => [newRequest, ...prev]);
    };

    const requestFullDeletion = async () => {
        if (!confirm('Are you sure you want to delete ALL your data? This cannot be undone.')) {
            return;
        }
        setDeletingAll(true);
        // Would call API
        await new Promise(resolve => setTimeout(resolve, 1000));
        requestDeletion(categories.map(c => c.id));
        setDeletingAll(false);
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed':
            case 'verified': return 'bg-green-500/20 text-green-300';
            case 'processing': return 'bg-yellow-500/20 text-yellow-300';
            case 'pending': return 'bg-blue-500/20 text-blue-300';
            default: return 'bg-white/20 text-white/70';
        }
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
                        <span className="text-4xl">⏱️</span>
                        Data Retention Settings
                    </h1>
                    <p className="text-white/60 mt-2">
                        Control how long we keep your data
                    </p>
                </div>
                <Link to="/my-data" className="btn-secondary">
                    ← Back
                </Link>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: 'Total Records', value: categories.reduce((sum, c) => sum + c.records_count, 0), icon: '📊' },
                    { label: 'Data Categories', value: categories.length, icon: '📁' },
                    { label: 'Deletion Requests', value: deletionRequests.length, icon: '🗑️' },
                    { label: 'Avg Retention', value: `${Math.round(categories.reduce((sum, c) => sum + c.current_retention_days, 0) / categories.length)} days`, icon: '⏱️' },
                ].map((stat, i) => (
                    <div key={i} className="glass rounded-lg p-4 text-center">
                        <span className="text-2xl">{stat.icon}</span>
                        <p className="text-2xl font-bold text-white mt-2">{stat.value}</p>
                        <p className="text-white/50 text-sm">{stat.label}</p>
                    </div>
                ))}
            </div>

            {/* Retention Settings by Category */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-6">Retention by Category</h2>
                <div className="space-y-6">
                    {categories.map(category => (
                        <div key={category.id} className="bg-white/5 rounded-lg p-4 border border-white/10">
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <h3 className="text-white font-medium">{category.name}</h3>
                                    <p className="text-white/50 text-sm mt-1">{category.description}</p>
                                    <div className="flex flex-wrap gap-2 mt-2">
                                        {category.data_types.map((type, i) => (
                                            <span key={i} className="bg-white/10 text-white/60 text-xs px-2 py-0.5 rounded">
                                                {type}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-white/60 text-sm">{category.records_count} records</p>
                                    <button
                                        onClick={() => requestDeletion([category.id])}
                                        className="text-red-400 hover:text-red-300 text-xs mt-1"
                                    >
                                        Delete Category
                                    </button>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-white/60">Retention Period</span>
                                    <span className="text-white font-medium">{category.current_retention_days} days</span>
                                </div>
                                <input
                                    type="range"
                                    min={category.min_days}
                                    max={category.max_days}
                                    value={category.current_retention_days}
                                    onChange={(e) => updateRetention(category.id, parseInt(e.target.value))}
                                    className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-purple-500"
                                />
                                <div className="flex justify-between text-xs text-white/40">
                                    <span>{category.min_days} days (min)</span>
                                    <span>{category.max_days} days (max)</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Deletion Requests */}
            {deletionRequests.length > 0 && (
                <div className="glass rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-white mb-4">Deletion Request History</h2>
                    <div className="space-y-3">
                        {deletionRequests.map(request => (
                            <div key={request.id} className="bg-white/5 rounded-lg p-4 flex items-center justify-between">
                                <div>
                                    <p className="text-white/80">
                                        {request.categories.join(', ')} data
                                    </p>
                                    <p className="text-white/50 text-sm">
                                        Requested: {formatDate(request.requested_at)}
                                        {request.completed_at && ` • Completed: ${formatDate(request.completed_at)}`}
                                    </p>
                                </div>
                                <span className={`px-3 py-1 rounded-full text-xs ${getStatusColor(request.status)}`}>
                                    {request.status}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Delete All Data */}
            <div className="glass rounded-xl p-6 border border-red-500/20">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                            <span className="text-red-400">⚠️</span>
                            Delete All My Data
                        </h2>
                        <p className="text-white/60 mt-1">
                            Request complete deletion of all your data. This action cannot be undone.
                        </p>
                    </div>
                    <button
                        onClick={requestFullDeletion}
                        disabled={deletingAll}
                        className="bg-red-500/20 text-red-300 hover:bg-red-500/30 px-6 py-2 rounded-lg transition-colors disabled:opacity-50"
                    >
                        {deletingAll ? 'Processing...' : 'Request Full Deletion'}
                    </button>
                </div>
                <p className="text-white/40 text-sm mt-4">
                    Deletion requests are processed within 30 days and verified across all downstream systems per 1033 requirements.
                </p>
            </div>

            {/* Compliance Note */}
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                <div className="flex items-start gap-3">
                    <span className="text-xl">🔒</span>
                    <div>
                        <h3 className="text-blue-300 font-medium">1033 Data Portability</h3>
                        <p className="text-white/60 text-sm mt-1">
                            Per CFPB regulations, we maintain your data for portability purposes. You can
                            export your data at any time before deletion, and we verify deletion across
                            all downstream systems.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RetentionSettingsPage;
