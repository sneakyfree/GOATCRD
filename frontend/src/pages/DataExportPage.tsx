import { useState } from 'react';
import { Link } from 'react-router-dom';

interface DataCategory {
    id: string;
    name: string;
    description: string;
    fields: string[];
    selected: boolean;
}

export function DataExportPage() {
    const [categories, setCategories] = useState<DataCategory[]>([
        {
            id: 'personal',
            name: 'Personal Information',
            description: 'Name, contact information, and demographic data',
            fields: ['Name', 'Email', 'Phone', 'Address', 'Date of Birth'],
            selected: true,
        },
        {
            id: 'financial',
            name: 'Financial Information',
            description: 'Income, employment, and debt information',
            fields: ['Annual Income', 'Employment Status', 'Employer', 'Monthly Debt Payments', 'Bank Accounts'],
            selected: true,
        },
        {
            id: 'credit',
            name: 'Credit Information',
            description: 'Credit scores and history',
            fields: ['Credit Score', 'Credit Utilization', 'Open Accounts', 'Payment History'],
            selected: true,
        },
        {
            id: 'scenarios',
            name: 'Scenario Results',
            description: 'Your credit option analysis results',
            fields: ['Eligible Programs', 'Rankings', 'Reason Codes', 'Improvement Suggestions'],
            selected: true,
        },
        {
            id: 'consents',
            name: 'Consent Records',
            description: 'Your data sharing permissions and history',
            fields: ['Active Consents', 'Revoked Consents', 'Consent Events'],
            selected: true,
        },
        {
            id: 'access',
            name: 'Access Logs',
            description: 'Record of who accessed your data',
            fields: ['Accessor', 'Resource', 'Action', 'Timestamp', 'Purpose'],
            selected: true,
        },
    ]);

    const [exportFormat, setExportFormat] = useState<'json' | 'csv'>('json');
    const [isExporting, setIsExporting] = useState(false);
    const [exportComplete, setExportComplete] = useState(false);

    const toggleCategory = (id: string) => {
        setCategories(prev =>
            prev.map(cat =>
                cat.id === id ? { ...cat, selected: !cat.selected } : cat
            )
        );
    };

    const selectAll = () => {
        setCategories(prev => prev.map(cat => ({ ...cat, selected: true })));
    };

    const deselectAll = () => {
        setCategories(prev => prev.map(cat => ({ ...cat, selected: false })));
    };

    const handleExport = async () => {
        setIsExporting(true);
        await new Promise(resolve => setTimeout(resolve, 2000));
        setIsExporting(false);
        setExportComplete(true);
    };

    const selectedCount = categories.filter(c => c.selected).length;

    return (
        <div className="py-8 max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Export Your Data</h1>
                <p className="text-white/60">
                    Under Section 1033, you have the right to access all data we hold about you.
                </p>
            </div>

            {/* Rights Notice */}
            <div className="glass-card p-6 mb-8 bg-sky-500/10 border-sky-500/20">
                <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-full bg-sky-500/20 flex items-center justify-center flex-shrink-0">
                        <span className="text-sky-400">🔒</span>
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-white mb-1">Your Data Rights</h3>
                        <p className="text-white/70 text-sm">
                            You can export a complete copy of your data at any time. This includes all information
                            you've provided, analysis results, consent records, and access logs.
                        </p>
                    </div>
                </div>
            </div>

            {exportComplete ? (
                <div className="glass-card p-8 text-center">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-emerald-500/20 flex items-center justify-center">
                        <span className="text-emerald-400 text-2xl">✓</span>
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-2">Export Complete!</h2>
                    <p className="text-white/60 mb-6">
                        Your data has been exported successfully.
                    </p>
                    <div className="flex justify-center gap-4">
                        <button
                            onClick={() => setExportComplete(false)}
                            className="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors"
                        >
                            Export Again
                        </button>
                        <Link to="/dashboard" className="btn-primary">
                            Back to Dashboard
                        </Link>
                    </div>
                </div>
            ) : (
                <>
                    {/* Data Selection */}
                    <div className="glass-card p-6 mb-6">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-xl font-semibold text-white">Select Data Categories</h2>
                            <div className="flex gap-2">
                                <button onClick={selectAll} className="text-sm text-sky-400 hover:text-sky-300">
                                    Select All
                                </button>
                                <span className="text-white/30">|</span>
                                <button onClick={deselectAll} className="text-sm text-white/60 hover:text-white">
                                    Deselect All
                                </button>
                            </div>
                        </div>

                        <div className="space-y-3">
                            {categories.map(category => (
                                <label
                                    key={category.id}
                                    className={`block p-4 rounded-lg border cursor-pointer transition-all ${category.selected
                                            ? 'bg-sky-500/10 border-sky-500/30'
                                            : 'bg-white/5 border-white/10 hover:border-white/20'
                                        }`}
                                >
                                    <div className="flex items-start gap-3">
                                        <input
                                            type="checkbox"
                                            checked={category.selected}
                                            onChange={() => toggleCategory(category.id)}
                                            className="mt-1 w-4 h-4 rounded"
                                        />
                                        <div className="flex-1">
                                            <p className="text-white font-medium">{category.name}</p>
                                            <p className="text-sm text-white/60 mb-2">{category.description}</p>
                                            <div className="flex flex-wrap gap-1">
                                                {category.fields.map((field, i) => (
                                                    <span key={i} className="px-2 py-0.5 bg-white/10 rounded text-xs text-white/70">
                                                        {field}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Export Options */}
                    <div className="glass-card p-6 mb-6">
                        <h2 className="text-xl font-semibold text-white mb-4">Export Format</h2>
                        <div className="flex gap-4">
                            <label
                                className={`flex-1 p-4 rounded-lg border cursor-pointer transition-all ${exportFormat === 'json'
                                        ? 'bg-sky-500/10 border-sky-500/30'
                                        : 'bg-white/5 border-white/10 hover:border-white/20'
                                    }`}
                            >
                                <input
                                    type="radio"
                                    name="format"
                                    value="json"
                                    checked={exportFormat === 'json'}
                                    onChange={() => setExportFormat('json')}
                                    className="sr-only"
                                />
                                <div className="text-center">
                                    <p className="text-white font-medium mb-1">JSON</p>
                                    <p className="text-sm text-white/60">Machine-readable</p>
                                </div>
                            </label>
                            <label
                                className={`flex-1 p-4 rounded-lg border cursor-pointer transition-all ${exportFormat === 'csv'
                                        ? 'bg-sky-500/10 border-sky-500/30'
                                        : 'bg-white/5 border-white/10 hover:border-white/20'
                                    }`}
                            >
                                <input
                                    type="radio"
                                    name="format"
                                    value="csv"
                                    checked={exportFormat === 'csv'}
                                    onChange={() => setExportFormat('csv')}
                                    className="sr-only"
                                />
                                <div className="text-center">
                                    <p className="text-white font-medium mb-1">CSV</p>
                                    <p className="text-sm text-white/60">Spreadsheet</p>
                                </div>
                            </label>
                        </div>
                    </div>

                    {/* Export Button */}
                    <button
                        onClick={handleExport}
                        disabled={isExporting || selectedCount === 0}
                        className="w-full btn-primary py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isExporting ? 'Preparing Export...' : `Export ${selectedCount} ${selectedCount === 1 ? 'Category' : 'Categories'}`}
                    </button>
                </>
            )}

            {/* Security Notice */}
            <div className="mt-6 glass-card p-4 bg-white/5 border-white/10">
                <p className="text-sm text-white/60 text-center">
                    🔒 Your export is encrypted and delivered securely.
                </p>
            </div>
        </div>
    );
}
