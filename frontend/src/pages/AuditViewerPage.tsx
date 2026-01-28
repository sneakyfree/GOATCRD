import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface AuditSnapshot {
    id: string;
    case_id: string;
    version: number;
    created_at: string;
    snapshot_hash: string;
    intake_data: object;
    scenarios_count: number;
    program_versions: Record<string, string>;
    rules_versions: Record<string, string>;
}

interface DeltaReport {
    snapshot_a: string;
    snapshot_b: string;
    rules_changed: string[];
    programs_changed: string[];
    outcomes_changed: Record<string, string>;
    reason: string;
}

interface ProgramVersionDelta {
    program_id: string;
    program_name: string;
    old_version: string;
    new_version: string;
    changes: VersionChange[];
    impact: 'breaking' | 'major' | 'minor' | 'patch';
    affected_cases: number;
}

interface VersionChange {
    type: 'rule_added' | 'rule_removed' | 'rule_modified' | 'threshold_changed' | 'state_coverage';
    field: string;
    old_value?: string;
    new_value?: string;
    description: string;
}

export function AuditViewerPage() {
    const [snapshots, setSnapshots] = useState<AuditSnapshot[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedSnapshot, setSelectedSnapshot] = useState<AuditSnapshot | null>(null);
    const [compareMode, setCompareMode] = useState(false);
    const [compareSnapshot, setCompareSnapshot] = useState<string | null>(null);
    const [deltaReport, setDeltaReport] = useState<DeltaReport | null>(null);
    const [viewMode, setViewMode] = useState<'snapshots' | 'versions'>('snapshots');

    // Mock Program Version Deltas
    const programDeltas: ProgramVersionDelta[] = [
        {
            program_id: 'prog-1',
            program_name: 'Standard Credit Card',
            old_version: 'v2.0',
            new_version: 'v2.1',
            impact: 'major',
            affected_cases: 1247,
            changes: [
                { type: 'threshold_changed', field: 'min_credit_score', old_value: '680', new_value: '700', description: 'Increased minimum credit score threshold' },
                { type: 'rule_added', field: 'bankruptcy_recent', new_value: 'true → NOT_ELIGIBLE', description: 'Added recent bankruptcy disqualification' },
                { type: 'state_coverage', field: 'allowed_states', old_value: '48 states', new_value: '50 states', description: 'Expanded to all 50 states' },
            ]
        },
        {
            program_id: 'prog-2',
            program_name: 'Personal Loan - Prime',
            old_version: 'v1.4',
            new_version: 'v1.5',
            impact: 'minor',
            affected_cases: 423,
            changes: [
                { type: 'rule_modified', field: 'max_dti', old_value: '0.40', new_value: '0.43', description: 'Relaxed DTI limit from 40% to 43%' },
            ]
        },
        {
            program_id: 'prog-3',
            program_name: 'FHA Mortgage',
            old_version: 'v3.1',
            new_version: 'v3.2',
            impact: 'patch',
            affected_cases: 89,
            changes: [
                { type: 'rule_modified', field: 'income_verification', old_value: 'required', new_value: 'conditional', description: 'Allow alternative documentation for self-employed' },
            ]
        },
    ];

    useEffect(() => {
        // In production, would get from URL params or context
        fetchSnapshots();
    }, []);

    const fetchSnapshots = async () => {
        try {
            // Mock data for demo
            const mockSnapshots: AuditSnapshot[] = [
                {
                    id: 'snap-001',
                    case_id: 'case-123',
                    version: 3,
                    created_at: new Date(Date.now() - 3600000).toISOString(),
                    snapshot_hash: 'a1b2c3d4e5f6',
                    intake_data: { income: 85000, credit_score: 720 },
                    scenarios_count: 4,
                    program_versions: { 'prog-1': 'v2.1', 'prog-2': 'v1.5' },
                    rules_versions: { 'ruleset-main': 'v3.0' }
                },
                {
                    id: 'snap-002',
                    case_id: 'case-123',
                    version: 2,
                    created_at: new Date(Date.now() - 86400000).toISOString(),
                    snapshot_hash: 'f6e5d4c3b2a1',
                    intake_data: { income: 80000, credit_score: 715 },
                    scenarios_count: 3,
                    program_versions: { 'prog-1': 'v2.0', 'prog-2': 'v1.5' },
                    rules_versions: { 'ruleset-main': 'v2.9' }
                },
                {
                    id: 'snap-003',
                    case_id: 'case-123',
                    version: 1,
                    created_at: new Date(Date.now() - 172800000).toISOString(),
                    snapshot_hash: 'deadbeef1234',
                    intake_data: { income: 80000, credit_score: 715 },
                    scenarios_count: 2,
                    program_versions: { 'prog-1': 'v2.0' },
                    rules_versions: { 'ruleset-main': 'v2.9' }
                }
            ];
            setSnapshots(mockSnapshots);
            // Case ID would come from URL params in production
        } catch (error) {
            console.error('Failed to fetch snapshots:', error);
        } finally {
            setLoading(false);
        }
    };

    const compareSnapshots = async (snapshotA: string, snapshotB: string) => {
        // Mock delta report
        setDeltaReport({
            snapshot_a: snapshotA,
            snapshot_b: snapshotB,
            rules_changed: ['max_dti_threshold', 'min_credit_score'],
            programs_changed: ['prog-1'],
            outcomes_changed: {
                'prog-1': 'REFER → ELIGIBLE',
                'prog-2': 'NOT_ELIGIBLE → REFER'
            },
            reason: 'Intake data updated and program rules version changed'
        });
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
                        <span className="text-4xl">📸</span>
                        Audit & Versioning
                    </h1>
                    <p className="text-white/60 mt-2">
                        Immutable decision records and program version tracking
                    </p>
                </div>
                <div className="flex gap-3">
                    {viewMode === 'snapshots' && (
                        <button
                            onClick={() => setCompareMode(!compareMode)}
                            className={`btn-secondary ${compareMode ? 'ring-2 ring-purple-500' : ''}`}
                        >
                            {compareMode ? '✓ Compare Mode' : 'Compare Snapshots'}
                        </button>
                    )}
                    <Link to="/dashboard" className="btn-secondary">
                        ← Back
                    </Link>
                </div>
            </div>

            {/* View Mode Tabs */}
            <div className="flex gap-2 border-b border-white/10 pb-2">
                <button
                    onClick={() => setViewMode('snapshots')}
                    className={`px-4 py-2 rounded-t-lg font-medium transition-colors ${viewMode === 'snapshots'
                        ? 'bg-purple-500/20 text-purple-400 border-b-2 border-purple-500'
                        : 'text-white/60 hover:text-white'
                        }`}
                >
                    📸 Audit Snapshots
                </button>
                <button
                    onClick={() => setViewMode('versions')}
                    className={`px-4 py-2 rounded-t-lg font-medium transition-colors ${viewMode === 'versions'
                        ? 'bg-blue-500/20 text-blue-400 border-b-2 border-blue-500'
                        : 'text-white/60 hover:text-white'
                        }`}
                >
                    📊 Program Version Deltas
                </button>
            </div>

            {/* Snapshots View */}
            {viewMode === 'snapshots' && (
                <>
                    {/* Compare Instructions */}
                    {compareMode && !deltaReport && (
                        <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
                            <p className="text-purple-300">
                                <span className="font-medium">Compare Mode Active:</span> Select two snapshots to compare.
                                Click a snapshot to select it, then click another to generate a delta report.
                            </p>
                        </div>
                    )}

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Snapshots Timeline */}
                        <div className="lg:col-span-1 glass rounded-xl p-6">
                            <h2 className="text-lg font-semibold text-white mb-4">Version History</h2>
                            <div className="relative">
                                <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-white/10" />
                                <div className="space-y-4">
                                    {snapshots.map((snapshot) => (
                                        <div
                                            key={snapshot.id}
                                            className={`relative pl-8 cursor-pointer transition-all ${selectedSnapshot?.id === snapshot.id
                                                ? 'scale-105'
                                                : 'hover:scale-102'
                                                }`}
                                            onClick={() => {
                                                if (compareMode) {
                                                    if (!compareSnapshot) {
                                                        setCompareSnapshot(snapshot.id);
                                                    } else if (compareSnapshot !== snapshot.id) {
                                                        compareSnapshots(compareSnapshot, snapshot.id);
                                                    }
                                                } else {
                                                    setSelectedSnapshot(snapshot);
                                                }
                                            }}
                                        >
                                            <div className={`absolute left-1 w-4 h-4 rounded-full ${selectedSnapshot?.id === snapshot.id || compareSnapshot === snapshot.id
                                                ? 'bg-purple-500'
                                                : 'bg-white/30'
                                                }`} />
                                            <div className={`bg-white/5 rounded-lg p-3 border ${selectedSnapshot?.id === snapshot.id
                                                ? 'border-purple-500'
                                                : compareSnapshot === snapshot.id
                                                    ? 'border-yellow-500'
                                                    : 'border-white/10'
                                                }`}>
                                                <div className="flex items-center justify-between">
                                                    <span className="text-white font-medium">v{snapshot.version}</span>
                                                    <span className="text-xs text-white/40">{snapshot.snapshot_hash.slice(0, 8)}</span>
                                                </div>
                                                <p className="text-white/50 text-sm mt-1">
                                                    {formatDate(snapshot.created_at)}
                                                </p>
                                                <p className="text-white/40 text-xs mt-1">
                                                    {snapshot.scenarios_count} scenarios
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Snapshot Detail or Delta Report */}
                        <div className="lg:col-span-2 glass rounded-xl p-6">
                            {deltaReport ? (
                                <>
                                    <div className="flex items-center justify-between mb-6">
                                        <h2 className="text-lg font-semibold text-white">Delta Report</h2>
                                        <button
                                            onClick={() => {
                                                setDeltaReport(null);
                                                setCompareSnapshot(null);
                                            }}
                                            className="text-white/60 hover:text-white"
                                        >
                                            ✕ Close
                                        </button>
                                    </div>

                                    <div className="space-y-6">
                                        {/* Outcome Changes */}
                                        <div>
                                            <h3 className="text-white/80 font-medium mb-3">Outcome Changes</h3>
                                            <div className="space-y-2">
                                                {Object.entries(deltaReport.outcomes_changed).map(([program, change]) => (
                                                    <div key={program} className="bg-white/5 rounded-lg p-3 flex items-center justify-between">
                                                        <span className="text-white/60">{program}</span>
                                                        <span className="text-yellow-300">{change}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Rules Changed */}
                                        {deltaReport.rules_changed.length > 0 && (
                                            <div>
                                                <h3 className="text-white/80 font-medium mb-3">Rules Changed</h3>
                                                <div className="flex flex-wrap gap-2">
                                                    {deltaReport.rules_changed.map(rule => (
                                                        <span key={rule} className="bg-red-500/20 text-red-300 px-3 py-1 rounded-full text-sm">
                                                            {rule}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Programs Changed */}
                                        {deltaReport.programs_changed.length > 0 && (
                                            <div>
                                                <h3 className="text-white/80 font-medium mb-3">Programs Changed</h3>
                                                <div className="flex flex-wrap gap-2">
                                                    {deltaReport.programs_changed.map(prog => (
                                                        <span key={prog} className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full text-sm">
                                                            {prog}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Reason */}
                                        <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
                                            <p className="text-purple-300">{deltaReport.reason}</p>
                                        </div>
                                    </div>
                                </>
                            ) : selectedSnapshot ? (
                                <>
                                    <h2 className="text-lg font-semibold text-white mb-6">
                                        Snapshot v{selectedSnapshot.version}
                                    </h2>

                                    <div className="space-y-6">
                                        {/* Metadata */}
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="bg-white/5 rounded-lg p-4">
                                                <p className="text-white/50 text-sm">Snapshot Hash</p>
                                                <p className="text-white font-mono">{selectedSnapshot.snapshot_hash}</p>
                                            </div>
                                            <div className="bg-white/5 rounded-lg p-4">
                                                <p className="text-white/50 text-sm">Created At</p>
                                                <p className="text-white">{formatDate(selectedSnapshot.created_at)}</p>
                                            </div>
                                        </div>

                                        {/* Intake Data */}
                                        <div>
                                            <h3 className="text-white/80 font-medium mb-3">Intake Data (at snapshot time)</h3>
                                            <pre className="bg-black/30 rounded-lg p-4 text-green-400 text-sm overflow-x-auto">
                                                {JSON.stringify(selectedSnapshot.intake_data, null, 2)}
                                            </pre>
                                        </div>

                                        {/* Version Pins */}
                                        <div>
                                            <h3 className="text-white/80 font-medium mb-3">Pinned Versions</h3>
                                            <div className="grid grid-cols-2 gap-4">
                                                <div className="bg-white/5 rounded-lg p-4">
                                                    <p className="text-white/50 text-sm mb-2">Programs</p>
                                                    {Object.entries(selectedSnapshot.program_versions).map(([id, ver]) => (
                                                        <div key={id} className="flex justify-between text-sm">
                                                            <span className="text-white/60">{id}</span>
                                                            <span className="text-white">{ver}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                                <div className="bg-white/5 rounded-lg p-4">
                                                    <p className="text-white/50 text-sm mb-2">Rulesets</p>
                                                    {Object.entries(selectedSnapshot.rules_versions).map(([id, ver]) => (
                                                        <div key={id} className="flex justify-between text-sm">
                                                            <span className="text-white/60">{id}</span>
                                                            <span className="text-white">{ver}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>

                                        {/* Determinism Guarantee */}
                                        <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                                            <div className="flex items-center gap-2">
                                                <span className="text-xl">✓</span>
                                                <p className="text-green-300">
                                                    <span className="font-medium">Determinism Guarantee:</span> Replaying this snapshot
                                                    will produce identical results. Hash: {selectedSnapshot.snapshot_hash}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <div className="flex flex-col items-center justify-center h-64 text-center">
                                    <div className="text-5xl mb-4">📋</div>
                                    <p className="text-white/60">Select a snapshot to view details</p>
                                    <p className="text-white/40 text-sm mt-2">
                                        Or enable Compare Mode to generate delta reports
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                </>
            )}

            {/* Program Version Deltas View */}
            {viewMode === 'versions' && (
                <div className="space-y-6">
                    {/* Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="glass rounded-xl p-4">
                            <div className="text-2xl font-bold text-white">{programDeltas.length}</div>
                            <div className="text-white/60 text-sm">Version Changes</div>
                        </div>
                        <div className="glass rounded-xl p-4">
                            <div className="text-2xl font-bold text-red-400">
                                {programDeltas.filter(d => d.impact === 'breaking').length}
                            </div>
                            <div className="text-white/60 text-sm">Breaking</div>
                        </div>
                        <div className="glass rounded-xl p-4">
                            <div className="text-2xl font-bold text-orange-400">
                                {programDeltas.filter(d => d.impact === 'major').length}
                            </div>
                            <div className="text-white/60 text-sm">Major</div>
                        </div>
                        <div className="glass rounded-xl p-4">
                            <div className="text-2xl font-bold text-blue-400">
                                {programDeltas.reduce((acc, d) => acc + d.affected_cases, 0).toLocaleString()}
                            </div>
                            <div className="text-white/60 text-sm">Affected Cases</div>
                        </div>
                    </div>

                    {/* Version Delta Cards */}
                    <div className="space-y-4">
                        {programDeltas.map(delta => (
                            <div key={delta.program_id} className="glass rounded-xl p-6">
                                <div className="flex items-start justify-between mb-4">
                                    <div>
                                        <h3 className="text-lg font-semibold text-white">{delta.program_name}</h3>
                                        <div className="flex items-center gap-2 mt-1">
                                            <span className="text-white/40 font-mono">{delta.old_version}</span>
                                            <span className="text-white/40">→</span>
                                            <span className="text-white font-mono">{delta.new_version}</span>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${delta.impact === 'breaking' ? 'bg-red-500/20 text-red-400' :
                                                delta.impact === 'major' ? 'bg-orange-500/20 text-orange-400' :
                                                    delta.impact === 'minor' ? 'bg-yellow-500/20 text-yellow-400' :
                                                        'bg-green-500/20 text-green-400'
                                            }`}>
                                            {delta.impact.toUpperCase()}
                                        </span>
                                        <span className="text-white/50 text-sm">
                                            {delta.affected_cases.toLocaleString()} cases affected
                                        </span>
                                    </div>
                                </div>

                                {/* Changes List */}
                                <div className="space-y-2">
                                    {delta.changes.map((change, i) => (
                                        <div key={i} className="bg-white/5 rounded-lg p-3 flex items-start gap-3">
                                            <span className={`text-xs px-2 py-1 rounded font-medium ${change.type === 'rule_added' ? 'bg-green-500/20 text-green-400' :
                                                    change.type === 'rule_removed' ? 'bg-red-500/20 text-red-400' :
                                                        change.type === 'threshold_changed' ? 'bg-orange-500/20 text-orange-400' :
                                                            'bg-blue-500/20 text-blue-400'
                                                }`}>
                                                {change.type.replace('_', ' ').toUpperCase()}
                                            </span>
                                            <div className="flex-1">
                                                <p className="text-white">{change.description}</p>
                                                {change.old_value && change.new_value && (
                                                    <p className="text-white/50 text-sm mt-1">
                                                        <span className="text-red-400 line-through">{change.old_value}</span>
                                                        {' → '}
                                                        <span className="text-green-400">{change.new_value}</span>
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default AuditViewerPage;
