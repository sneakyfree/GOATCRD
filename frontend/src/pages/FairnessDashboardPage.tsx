import { useState, useMemo } from 'react';

// Types
interface FairnessTest {
    id: string;
    test_type: 'disparate_impact' | 'lda_search' | 'feature_audit';
    model_version: string;
    rules_version: string;
    passed: boolean;
    metrics: Record<string, number>;
    run_at: string;
    approved_by?: string;
    artifacts: string[];
}

interface DisparateImpactResult {
    group: string;
    baseline_rate: number;
    comparison_rate: number;
    ratio: number;
    threshold: number;
    passed: boolean;
}

// Mock data
const MOCK_TESTS: FairnessTest[] = [
    {
        id: '1',
        test_type: 'disparate_impact',
        model_version: 'v2.3.1',
        rules_version: '4',
        passed: true,
        metrics: {
            'age_proxy': 0.87,
            'zip_proxy': 0.82,
            'income_tier': 0.91,
        },
        run_at: '2026-01-27T10:00:00Z',
        approved_by: 'compliance@goatcrd.com',
        artifacts: ['di_report_v2.3.1.json'],
    },
    {
        id: '2',
        test_type: 'lda_search',
        model_version: 'v2.3.1',
        rules_version: '4',
        passed: true,
        metrics: {
            'alternatives_found': 3,
            'best_alternative_impact': 0.02,
        },
        run_at: '2026-01-27T09:45:00Z',
        artifacts: ['lda_alternatives_v2.3.1.json'],
    },
    {
        id: '3',
        test_type: 'feature_audit',
        model_version: 'v2.3.1',
        rules_version: '4',
        passed: true,
        metrics: {
            'features_audited': 24,
            'proxy_flags': 0,
        },
        run_at: '2026-01-27T09:30:00Z',
        artifacts: ['feature_audit_v2.3.1.json'],
    },
    {
        id: '4',
        test_type: 'disparate_impact',
        model_version: 'v2.2.0',
        rules_version: '3',
        passed: false,
        metrics: {
            'age_proxy': 0.78,
            'zip_proxy': 0.69,
            'income_tier': 0.88,
        },
        run_at: '2026-01-15T14:00:00Z',
        artifacts: ['di_report_v2.2.0.json'],
    },
];

const MOCK_DI_RESULTS: DisparateImpactResult[] = [
    { group: 'Age Proxy (55+)', baseline_rate: 0.72, comparison_rate: 0.63, ratio: 0.87, threshold: 0.80, passed: true },
    { group: 'Zip Code Proxy', baseline_rate: 0.68, comparison_rate: 0.56, ratio: 0.82, threshold: 0.80, passed: true },
    { group: 'Income Tier (Low)', baseline_rate: 0.65, comparison_rate: 0.59, ratio: 0.91, threshold: 0.80, passed: true },
    { group: 'Education Proxy', baseline_rate: 0.70, comparison_rate: 0.64, ratio: 0.91, threshold: 0.80, passed: true },
];

const MOCK_TRENDS = [
    { date: '2026-01-21', overall: 0.85, age: 0.82, zip: 0.79, income: 0.88 },
    { date: '2026-01-22', overall: 0.86, age: 0.84, zip: 0.80, income: 0.89 },
    { date: '2026-01-23', overall: 0.87, age: 0.85, zip: 0.81, income: 0.90 },
    { date: '2026-01-24', overall: 0.86, age: 0.86, zip: 0.80, income: 0.89 },
    { date: '2026-01-25', overall: 0.88, age: 0.87, zip: 0.82, income: 0.91 },
    { date: '2026-01-26', overall: 0.87, age: 0.86, zip: 0.81, income: 0.90 },
    { date: '2026-01-27', overall: 0.88, age: 0.87, zip: 0.82, income: 0.91 },
];

export default function FairnessDashboardPage() {
    const [tests, setTests] = useState<FairnessTest[]>(MOCK_TESTS);
    const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('7d');
    const [selectedTest, setSelectedTest] = useState<FairnessTest | null>(null);
    const [showRunDialog, setShowRunDialog] = useState(false);

    const latestTest = useMemo(() =>
        tests.filter(t => t.test_type === 'disparate_impact').sort((a, b) =>
            new Date(b.run_at).getTime() - new Date(a.run_at).getTime()
        )[0],
        [tests]);

    const passRate = useMemo(() => {
        const recent = tests.filter(t => t.test_type === 'disparate_impact');
        const passed = recent.filter(t => t.passed).length;
        return recent.length > 0 ? (passed / recent.length * 100) : 0;
    }, [tests]);

    const overallStatus = latestTest?.passed ?? false;

    const handleRunTests = () => {
        // Mock running new tests
        const newTest: FairnessTest = {
            id: Date.now().toString(),
            test_type: 'disparate_impact',
            model_version: 'v2.3.2',
            rules_version: '4',
            passed: true,
            metrics: {
                'age_proxy': 0.88,
                'zip_proxy': 0.83,
                'income_tier': 0.92,
            },
            run_at: new Date().toISOString(),
            artifacts: ['di_report_v2.3.2.json'],
        };
        setTests(prev => [newTest, ...prev]);
        setShowRunDialog(false);
    };

    return (
        <div className="min-h-screen bg-slate-900 text-white">
            {/* Header */}
            <div className="bg-slate-800/50 border-b border-slate-700 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl font-bold">Fairness Dashboard</h1>
                            <p className="text-slate-400 text-sm">DNA Strand Law 5: Fairness is Mandatory</p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={() => setShowRunDialog(true)}
                                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                            >
                                ▶️ Run Tests
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 py-6">
                {/* Overall Status Card */}
                <div className={`rounded-xl p-6 mb-6 ${overallStatus ? 'bg-green-500/10 border border-green-500/30' : 'bg-red-500/10 border border-red-500/30'}`}>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className={`w-16 h-16 rounded-full flex items-center justify-center text-3xl ${overallStatus ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                                {overallStatus ? '✅' : '❌'}
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold">
                                    {overallStatus ? 'Fairness Tests Passing' : 'Fairness Tests Failing'}
                                </h2>
                                <p className="text-slate-400">
                                    Last run: {latestTest ? new Date(latestTest.run_at).toLocaleString() : 'Never'}
                                </p>
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-4xl font-bold">{passRate.toFixed(0)}%</div>
                            <div className="text-slate-400 text-sm">Pass Rate (All Time)</div>
                        </div>
                    </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-slate-400 text-sm mb-1">Disparate Impact Ratio</div>
                        <div className="text-2xl font-bold">
                            {latestTest?.metrics?.age_proxy ? (Object.values(latestTest.metrics).reduce((a, b) => a + b, 0) / Object.values(latestTest.metrics).length).toFixed(2) : '—'}
                        </div>
                        <div className="text-green-400 text-sm">Threshold: ≥ 0.80</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-slate-400 text-sm mb-1">LDA Alternatives</div>
                        <div className="text-2xl font-bold">
                            {tests.find(t => t.test_type === 'lda_search')?.metrics?.alternatives_found ?? '—'}
                        </div>
                        <div className="text-slate-500 text-sm">Found & Documented</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-slate-400 text-sm mb-1">Features Audited</div>
                        <div className="text-2xl font-bold">
                            {tests.find(t => t.test_type === 'feature_audit')?.metrics?.features_audited ?? '—'}
                        </div>
                        <div className="text-slate-500 text-sm">No Proxy Flags</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-slate-400 text-sm mb-1">CI/CD Gate</div>
                        <div className="text-2xl font-bold text-green-400">Active</div>
                        <div className="text-slate-500 text-sm">Blocking on Failure</div>
                    </div>
                </div>

                {/* Time Range Selector */}
                <div className="flex gap-2 mb-6">
                    {(['7d', '30d', '90d'] as const).map(range => (
                        <button
                            key={range}
                            onClick={() => setTimeRange(range)}
                            className={`px-4 py-2 rounded-lg font-medium transition-colors ${timeRange === range
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-slate-800 text-slate-400 hover:text-white'
                                }`}
                        >
                            {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
                        </button>
                    ))}
                </div>

                {/* Disparate Impact Chart (Mock) */}
                <div className="bg-slate-800 rounded-lg p-6 mb-6">
                    <h3 className="text-lg font-semibold mb-4">Disparate Impact Ratio Trend</h3>
                    <div className="h-48 flex items-end gap-2">
                        {MOCK_TRENDS.map((day, i) => (
                            <div key={i} className="flex-1 flex flex-col items-center gap-1">
                                <div
                                    className="w-full bg-blue-500 rounded-t"
                                    style={{ height: `${day.overall * 150}px` }}
                                />
                                <span className="text-xs text-slate-500">{day.date.split('-')[2]}</span>
                            </div>
                        ))}
                    </div>
                    <div className="flex justify-between mt-2">
                        <div className="flex gap-4 text-sm">
                            <span className="flex items-center gap-1"><span className="w-3 h-3 bg-blue-500 rounded" /> Overall</span>
                        </div>
                        <div className="text-sm text-slate-500">
                            Threshold: 0.80 (shown as red line in production)
                        </div>
                    </div>
                </div>

                {/* Disparate Impact Results Table */}
                <div className="bg-slate-800 rounded-lg overflow-hidden mb-6">
                    <div className="p-4 border-b border-slate-700">
                        <h3 className="text-lg font-semibold">Disparate Impact Analysis</h3>
                        <p className="text-slate-400 text-sm">Approval rate ratios across demographic proxies</p>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-slate-900/50">
                                <tr>
                                    <th className="text-left px-4 py-3 text-sm font-medium text-slate-400">Group</th>
                                    <th className="text-right px-4 py-3 text-sm font-medium text-slate-400">Baseline Rate</th>
                                    <th className="text-right px-4 py-3 text-sm font-medium text-slate-400">Comparison Rate</th>
                                    <th className="text-right px-4 py-3 text-sm font-medium text-slate-400">Ratio</th>
                                    <th className="text-right px-4 py-3 text-sm font-medium text-slate-400">Threshold</th>
                                    <th className="text-center px-4 py-3 text-sm font-medium text-slate-400">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {MOCK_DI_RESULTS.map((result, i) => (
                                    <tr key={i} className="border-t border-slate-700">
                                        <td className="px-4 py-3 font-medium">{result.group}</td>
                                        <td className="px-4 py-3 text-right text-slate-400">{(result.baseline_rate * 100).toFixed(1)}%</td>
                                        <td className="px-4 py-3 text-right text-slate-400">{(result.comparison_rate * 100).toFixed(1)}%</td>
                                        <td className="px-4 py-3 text-right font-mono font-medium">{result.ratio.toFixed(2)}</td>
                                        <td className="px-4 py-3 text-right text-slate-500">{result.threshold.toFixed(2)}</td>
                                        <td className="px-4 py-3 text-center">
                                            {result.passed ? (
                                                <span className="text-green-400">✅ Pass</span>
                                            ) : (
                                                <span className="text-red-400">❌ Fail</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Test History */}
                <div className="bg-slate-800 rounded-lg overflow-hidden">
                    <div className="p-4 border-b border-slate-700">
                        <h3 className="text-lg font-semibold">Test History</h3>
                    </div>
                    <div className="divide-y divide-slate-700">
                        {tests.map(test => (
                            <div
                                key={test.id}
                                onClick={() => setSelectedTest(test)}
                                className="p-4 flex items-center justify-between hover:bg-slate-700/50 cursor-pointer transition-colors"
                            >
                                <div className="flex items-center gap-4">
                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${test.passed ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                        {test.passed ? '✓' : '✕'}
                                    </div>
                                    <div>
                                        <div className="font-medium">
                                            {test.test_type === 'disparate_impact' ? 'Disparate Impact Test' :
                                                test.test_type === 'lda_search' ? 'LDA Search' : 'Feature Audit'}
                                        </div>
                                        <div className="text-sm text-slate-400">
                                            Model {test.model_version} • Rules v{test.rules_version}
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm text-slate-400">
                                        {new Date(test.run_at).toLocaleString()}
                                    </div>
                                    {test.approved_by && (
                                        <div className="text-xs text-green-400">
                                            Approved by {test.approved_by}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Run Tests Dialog */}
            {showRunDialog && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-800 rounded-xl w-full max-w-md">
                        <div className="p-4 border-b border-slate-700">
                            <h2 className="text-xl font-semibold">Run Fairness Tests</h2>
                        </div>
                        <div className="p-4 space-y-4">
                            <div className="space-y-2">
                                <label className="flex items-center gap-3">
                                    <input type="checkbox" className="w-5 h-5 rounded" defaultChecked />
                                    <span>Disparate Impact (Required)</span>
                                </label>
                                <label className="flex items-center gap-3">
                                    <input type="checkbox" className="w-5 h-5 rounded" defaultChecked />
                                    <span>LDA Search</span>
                                </label>
                                <label className="flex items-center gap-3">
                                    <input type="checkbox" className="w-5 h-5 rounded" defaultChecked />
                                    <span>Feature Audit</span>
                                </label>
                            </div>
                            <p className="text-sm text-slate-400">
                                Tests will run against current model v2.3.2 and rules v4.
                            </p>
                        </div>
                        <div className="p-4 border-t border-slate-700 flex justify-end gap-3">
                            <button
                                onClick={() => setShowRunDialog(false)}
                                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleRunTests}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium"
                            >
                                Run Tests
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Test Detail Modal */}
            {selectedTest && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-800 rounded-xl w-full max-w-lg">
                        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                            <h2 className="text-xl font-semibold">Test Details</h2>
                            <button
                                onClick={() => setSelectedTest(null)}
                                className="p-2 hover:bg-slate-700 rounded-lg"
                            >
                                ✕
                            </button>
                        </div>
                        <div className="p-4 space-y-4">
                            <div className={`rounded-lg p-3 ${selectedTest.passed ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                                <div className="font-medium">
                                    {selectedTest.passed ? '✅ Test Passed' : '❌ Test Failed'}
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <div className="text-slate-400">Test Type</div>
                                    <div className="font-medium">{selectedTest.test_type}</div>
                                </div>
                                <div>
                                    <div className="text-slate-400">Run At</div>
                                    <div className="font-medium">{new Date(selectedTest.run_at).toLocaleString()}</div>
                                </div>
                                <div>
                                    <div className="text-slate-400">Model Version</div>
                                    <div className="font-medium">{selectedTest.model_version}</div>
                                </div>
                                <div>
                                    <div className="text-slate-400">Rules Version</div>
                                    <div className="font-medium">v{selectedTest.rules_version}</div>
                                </div>
                            </div>

                            <div>
                                <div className="text-slate-400 text-sm mb-2">Metrics</div>
                                <div className="bg-slate-900 rounded-lg p-3 font-mono text-sm">
                                    {Object.entries(selectedTest.metrics).map(([key, value]) => (
                                        <div key={key} className="flex justify-between">
                                            <span className="text-slate-400">{key}:</span>
                                            <span>{value}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <div className="text-slate-400 text-sm mb-2">Artifacts</div>
                                <div className="space-y-1">
                                    {selectedTest.artifacts.map((artifact, i) => (
                                        <div key={i} className="flex items-center gap-2 text-blue-400 hover:underline cursor-pointer">
                                            📄 {artifact}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
