import { useState } from 'react';
import { Link } from 'react-router-dom';

interface FairnessArtifact {
    id: string;
    run_id: string;
    created_at: string;
    status: 'passed' | 'failed' | 'warning';
    commit_sha: string;
    branch: string;
    metrics: {
        disparate_impact: number;
        statistical_parity: number;
        equal_opportunity: number;
    };
    protected_attributes: string[];
    file_path: string;
}

const MOCK_ARTIFACTS: FairnessArtifact[] = [
    {
        id: 'art-001',
        run_id: 'run-12345',
        created_at: new Date(Date.now() - 3600000).toISOString(),
        status: 'passed',
        commit_sha: 'a1b2c3d',
        branch: 'main',
        metrics: { disparate_impact: 0.85, statistical_parity: 0.92, equal_opportunity: 0.88 },
        protected_attributes: ['age', 'gender', 'race', 'ethnicity'],
        file_path: '/ci/artifacts/fairness-report-001.json'
    },
    {
        id: 'art-002',
        run_id: 'run-12344',
        created_at: new Date(Date.now() - 86400000).toISOString(),
        status: 'warning',
        commit_sha: 'f4e5d6c',
        branch: 'feature/rule-update',
        metrics: { disparate_impact: 0.78, statistical_parity: 0.81, equal_opportunity: 0.75 },
        protected_attributes: ['age', 'gender', 'race'],
        file_path: '/ci/artifacts/fairness-report-002.json'
    },
    {
        id: 'art-003',
        run_id: 'run-12343',
        created_at: new Date(Date.now() - 172800000).toISOString(),
        status: 'failed',
        commit_sha: 'g7h8i9j',
        branch: 'feature/new-model',
        metrics: { disparate_impact: 0.62, statistical_parity: 0.58, equal_opportunity: 0.55 },
        protected_attributes: ['age', 'gender', 'race', 'ethnicity', 'disability'],
        file_path: '/ci/artifacts/fairness-report-003.json'
    },
];

export default function FairnessArtifactViewer() {
    const [artifacts] = useState<FairnessArtifact[]>(MOCK_ARTIFACTS);
    const [selectedArtifact, setSelectedArtifact] = useState<FairnessArtifact | null>(null);
    const [filterStatus, setFilterStatus] = useState<string>('all');

    const filteredArtifacts = artifacts.filter(a =>
        filterStatus === 'all' || a.status === filterStatus
    );

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'passed': return 'bg-green-500/20 text-green-400';
            case 'warning': return 'bg-yellow-500/20 text-yellow-400';
            case 'failed': return 'bg-red-500/20 text-red-400';
            default: return 'bg-white/20 text-white/60';
        }
    };

    const getMetricColor = (value: number, threshold: number = 0.8) => {
        if (value >= threshold) return 'text-green-400';
        if (value >= 0.7) return 'text-yellow-400';
        return 'text-red-400';
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                        <span className="text-4xl">📦</span>
                        Fairness Test Artifacts
                    </h1>
                    <p className="text-white/60 mt-2">
                        CI/CD fairness test results and downloadable reports
                    </p>
                </div>
                <Link to="/admin/fairness" className="btn-secondary">
                    ← Back to Dashboard
                </Link>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="glass rounded-xl p-4">
                    <div className="text-2xl font-bold text-white">{artifacts.length}</div>
                    <div className="text-white/60 text-sm">Total Artifacts</div>
                </div>
                <div className="glass rounded-xl p-4">
                    <div className="text-2xl font-bold text-green-400">
                        {artifacts.filter(a => a.status === 'passed').length}
                    </div>
                    <div className="text-white/60 text-sm">Passed</div>
                </div>
                <div className="glass rounded-xl p-4">
                    <div className="text-2xl font-bold text-yellow-400">
                        {artifacts.filter(a => a.status === 'warning').length}
                    </div>
                    <div className="text-white/60 text-sm">Warnings</div>
                </div>
                <div className="glass rounded-xl p-4">
                    <div className="text-2xl font-bold text-red-400">
                        {artifacts.filter(a => a.status === 'failed').length}
                    </div>
                    <div className="text-white/60 text-sm">Failed</div>
                </div>
            </div>

            {/* Filters */}
            <div className="flex gap-2">
                {['all', 'passed', 'warning', 'failed'].map(status => (
                    <button
                        key={status}
                        onClick={() => setFilterStatus(status)}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${filterStatus === status
                                ? 'bg-purple-500 text-white'
                                : 'bg-white/10 text-white/60 hover:text-white'
                            }`}
                    >
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                    </button>
                ))}
            </div>

            {/* Grid Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Artifacts List */}
                <div className="lg:col-span-1 space-y-3">
                    {filteredArtifacts.map(artifact => (
                        <div
                            key={artifact.id}
                            onClick={() => setSelectedArtifact(artifact)}
                            className={`glass rounded-xl p-4 cursor-pointer transition-all ${selectedArtifact?.id === artifact.id
                                    ? 'ring-2 ring-purple-500'
                                    : 'hover:bg-white/10'
                                }`}
                        >
                            <div className="flex items-center justify-between mb-2">
                                <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(artifact.status)}`}>
                                    {artifact.status.toUpperCase()}
                                </span>
                                <span className="text-white/40 text-xs font-mono">{artifact.commit_sha}</span>
                            </div>
                            <p className="text-white font-medium">{artifact.branch}</p>
                            <p className="text-white/50 text-sm">{formatDate(artifact.created_at)}</p>
                        </div>
                    ))}
                </div>

                {/* Artifact Detail */}
                <div className="lg:col-span-2 glass rounded-xl p-6">
                    {selectedArtifact ? (
                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h2 className="text-xl font-semibold text-white">{selectedArtifact.branch}</h2>
                                    <p className="text-white/50">Run ID: {selectedArtifact.run_id}</p>
                                </div>
                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedArtifact.status)}`}>
                                    {selectedArtifact.status.toUpperCase()}
                                </span>
                            </div>

                            {/* Metrics Grid */}
                            <div>
                                <h3 className="text-white/80 font-medium mb-3">Fairness Metrics</h3>
                                <div className="grid grid-cols-3 gap-4">
                                    <div className="bg-white/5 rounded-lg p-4">
                                        <p className="text-white/50 text-sm">Disparate Impact</p>
                                        <p className={`text-2xl font-bold ${getMetricColor(selectedArtifact.metrics.disparate_impact)}`}>
                                            {(selectedArtifact.metrics.disparate_impact * 100).toFixed(1)}%
                                        </p>
                                        <p className="text-white/40 text-xs mt-1">Threshold: ≥80%</p>
                                    </div>
                                    <div className="bg-white/5 rounded-lg p-4">
                                        <p className="text-white/50 text-sm">Statistical Parity</p>
                                        <p className={`text-2xl font-bold ${getMetricColor(selectedArtifact.metrics.statistical_parity)}`}>
                                            {(selectedArtifact.metrics.statistical_parity * 100).toFixed(1)}%
                                        </p>
                                        <p className="text-white/40 text-xs mt-1">Threshold: ≥80%</p>
                                    </div>
                                    <div className="bg-white/5 rounded-lg p-4">
                                        <p className="text-white/50 text-sm">Equal Opportunity</p>
                                        <p className={`text-2xl font-bold ${getMetricColor(selectedArtifact.metrics.equal_opportunity)}`}>
                                            {(selectedArtifact.metrics.equal_opportunity * 100).toFixed(1)}%
                                        </p>
                                        <p className="text-white/40 text-xs mt-1">Threshold: ≥80%</p>
                                    </div>
                                </div>
                            </div>

                            {/* Protected Attributes */}
                            <div>
                                <h3 className="text-white/80 font-medium mb-3">Protected Attributes Tested</h3>
                                <div className="flex flex-wrap gap-2">
                                    {selectedArtifact.protected_attributes.map(attr => (
                                        <span key={attr} className="px-3 py-1 bg-white/10 rounded-full text-white/80 text-sm">
                                            {attr}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Artifact Info */}
                            <div className="bg-white/5 rounded-lg p-4">
                                <h3 className="text-white/80 font-medium mb-2">Artifact Details</h3>
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <span className="text-white/50">Commit SHA:</span>
                                        <span className="text-white ml-2 font-mono">{selectedArtifact.commit_sha}</span>
                                    </div>
                                    <div>
                                        <span className="text-white/50">Created:</span>
                                        <span className="text-white ml-2">{formatDate(selectedArtifact.created_at)}</span>
                                    </div>
                                    <div className="col-span-2">
                                        <span className="text-white/50">File Path:</span>
                                        <span className="text-white ml-2 font-mono text-xs">{selectedArtifact.file_path}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="flex gap-3">
                                <button className="btn-primary flex-1">
                                    📥 Download Report
                                </button>
                                <button className="btn-secondary">
                                    🔗 View in CI
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-64 text-center">
                            <div className="text-5xl mb-4">📦</div>
                            <p className="text-white/60">Select an artifact to view details</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
