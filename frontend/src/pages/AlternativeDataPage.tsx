import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const API_URL = '/api/v1';

interface ConnectedAccount {
    id: string;
    institution_name: string;
    account_name: string;
    account_type: string;
    account_mask: string;
    balance: number | null;
    connected_at: string;
    status: string;
}

interface CashFlowAnalysis {
    avg_monthly_income: number;
    avg_monthly_expenses: number;
    net_monthly_cash_flow: number;
    savings_rate: number;
    income_volatility: number;
    income_sources: Array<{ source: string; total: number; count: number }>;
    risk_indicators: {
        overdraft_count: number;
        nsf_count: number;
        avg_low_balance_days: number;
    };
    confidence: number;
}

export function AlternativeDataPage() {
    const { accessToken } = useAuthStore();
    const [accounts, setAccounts] = useState<ConnectedAccount[]>([]);
    const [loading, setLoading] = useState(true);
    const [connecting, setConnecting] = useState(false);
    const [selectedAccount, setSelectedAccount] = useState<string | null>(null);
    const [cashFlow, setCashFlow] = useState<CashFlowAnalysis | null>(null);
    const [cashFlowLoading, setCashFlowLoading] = useState(false);

    useEffect(() => {
        fetchAccounts();
    }, []);

    const fetchAccounts = async () => {
        try {
            const response = await fetch(`${API_URL}/alt-data/accounts`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });
            const data = await response.json();
            setAccounts(data.accounts || []);
        } catch (error) {
            console.error('Failed to fetch accounts:', error);
        } finally {
            setLoading(false);
        }
    };

    const initiateConnection = async () => {
        setConnecting(true);
        try {
            // Get link token
            await fetch(`${API_URL}/alt-data/link-token`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });

            // In production, would use Plaid Link SDK here
            // For demo, simulate successful connection
            const mockExchange = {
                public_token: `public-sandbox-${Date.now()}`,
                institution_id: 'ins_1',
                institution_name: 'Demo Bank',
                accounts: [{
                    name: 'Checking Account',
                    type: 'depository',
                    mask: '4567',
                    balance: 5234.50
                }]
            };

            const exchangeResponse = await fetch(`${API_URL}/alt-data/exchange`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(mockExchange)
            });

            if (exchangeResponse.ok) {
                await fetchAccounts();
            }
        } catch (error) {
            console.error('Failed to connect account:', error);
        } finally {
            setConnecting(false);
        }
    };

    const disconnectAccount = async (accountId: string) => {
        try {
            await fetch(`${API_URL}/alt-data/accounts/${accountId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });
            setAccounts(accounts.filter(a => a.id !== accountId));
            if (selectedAccount === accountId) {
                setSelectedAccount(null);
                setCashFlow(null);
            }
        } catch (error) {
            console.error('Failed to disconnect:', error);
        }
    };

    const loadCashFlow = async (accountId: string) => {
        setSelectedAccount(accountId);
        setCashFlowLoading(true);
        try {
            const response = await fetch(`${API_URL}/alt-data/accounts/${accountId}/cash-flow`, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });
            const data = await response.json();
            setCashFlow(data);
        } catch (error) {
            console.error('Failed to load cash flow:', error);
        } finally {
            setCashFlowLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'bg-green-500/20 text-green-300';
            case 'pending': return 'bg-yellow-500/20 text-yellow-300';
            case 'error': return 'bg-red-500/20 text-red-300';
            default: return 'bg-gray-500/20 text-gray-300';
        }
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
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
                    <h1 className="text-3xl font-bold text-white">Alternative Data</h1>
                    <p className="text-white/60 mt-2">
                        Connect bank accounts and alternative data sources for better credit assessment
                    </p>
                </div>
                <Link to="/dashboard" className="btn-secondary">
                    ← Back to Dashboard
                </Link>
            </div>

            {/* Connect New Account */}
            <div className="glass rounded-xl p-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                            <span className="text-2xl">🏦</span>
                            Connect Bank Account
                        </h2>
                        <p className="text-white/60 mt-1">
                            Securely link your bank account via Plaid to unlock additional scenarios
                        </p>
                    </div>
                    <button
                        onClick={initiateConnection}
                        disabled={connecting}
                        className="btn-primary flex items-center gap-2"
                    >
                        {connecting ? (
                            <>
                                <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-white"></div>
                                Connecting...
                            </>
                        ) : (
                            <>
                                <span>+</span>
                                Connect Account
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Connected Accounts */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Connected Accounts</h2>

                {accounts.length === 0 ? (
                    <div className="text-center py-8">
                        <div className="text-4xl mb-3">🔗</div>
                        <p className="text-white/60">No accounts connected yet</p>
                        <p className="text-white/40 text-sm mt-1">
                            Connect a bank account to get cash flow analysis and unlock more scenarios
                        </p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {accounts.map(account => (
                            <div
                                key={account.id}
                                className={`bg-white/5 rounded-lg p-4 border transition-colors cursor-pointer ${selectedAccount === account.id
                                    ? 'border-purple-500'
                                    : 'border-white/10 hover:border-white/20'
                                    }`}
                                onClick={() => loadCashFlow(account.id)}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                                            {account.institution_name.charAt(0)}
                                        </div>
                                        <div>
                                            <h3 className="text-white font-medium">
                                                {account.institution_name}
                                            </h3>
                                            <p className="text-white/60 text-sm">
                                                {account.account_name} •••• {account.account_mask}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="text-right">
                                            <p className="text-white font-semibold">
                                                {account.balance !== null ? formatCurrency(account.balance) : '—'}
                                            </p>
                                            <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(account.status)}`}>
                                                {account.status}
                                            </span>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                disconnectAccount(account.id);
                                            }}
                                            className="text-red-400 hover:text-red-300 p-2"
                                            title="Disconnect account"
                                        >
                                            ✕
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Cash Flow Analysis */}
            {selectedAccount && (
                <div className="glass rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                        <span>📊</span>
                        Cash Flow Analysis
                    </h2>

                    {cashFlowLoading ? (
                        <div className="flex items-center justify-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-purple-500"></div>
                        </div>
                    ) : cashFlow ? (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Income */}
                            <div className="bg-green-500/10 rounded-lg p-4 border border-green-500/20">
                                <p className="text-green-300 text-sm font-medium">Avg Monthly Income</p>
                                <p className="text-2xl font-bold text-white mt-1">
                                    {formatCurrency(cashFlow.avg_monthly_income)}
                                </p>
                                <div className="mt-2 text-sm text-white/60">
                                    Volatility: {(cashFlow.income_volatility * 100).toFixed(0)}%
                                </div>
                            </div>

                            {/* Expenses */}
                            <div className="bg-red-500/10 rounded-lg p-4 border border-red-500/20">
                                <p className="text-red-300 text-sm font-medium">Avg Monthly Expenses</p>
                                <p className="text-2xl font-bold text-white mt-1">
                                    {formatCurrency(cashFlow.avg_monthly_expenses)}
                                </p>
                                <div className="mt-2 text-sm text-white/60">
                                    Ratio: {(cashFlow.avg_monthly_expenses / cashFlow.avg_monthly_income * 100).toFixed(0)}%
                                </div>
                            </div>

                            {/* Net Cash Flow */}
                            <div className="bg-purple-500/10 rounded-lg p-4 border border-purple-500/20">
                                <p className="text-purple-300 text-sm font-medium">Net Monthly Cash Flow</p>
                                <p className={`text-2xl font-bold mt-1 ${cashFlow.net_monthly_cash_flow >= 0 ? 'text-green-400' : 'text-red-400'
                                    }`}>
                                    {formatCurrency(cashFlow.net_monthly_cash_flow)}
                                </p>
                                <div className="mt-2 text-sm text-white/60">
                                    Savings Rate: {(cashFlow.savings_rate * 100).toFixed(0)}%
                                </div>
                            </div>

                            {/* Income Sources */}
                            <div className="md:col-span-2 bg-white/5 rounded-lg p-4 border border-white/10">
                                <p className="text-white/80 font-medium mb-3">Income Sources</p>
                                <div className="space-y-2">
                                    {cashFlow.income_sources.map((source, i) => (
                                        <div key={i} className="flex items-center justify-between">
                                            <span className="text-white/60 capitalize">{source.source.replace('_', ' ')}</span>
                                            <span className="text-white font-medium">{formatCurrency(source.total)}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Confidence */}
                            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                                <p className="text-white/80 font-medium mb-3">Analysis Confidence</p>
                                <div className="flex items-center gap-3">
                                    <div className="flex-1 h-3 bg-white/10 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full rounded-full ${cashFlow.confidence >= 80 ? 'bg-green-500' :
                                                cashFlow.confidence >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                                                }`}
                                            style={{ width: `${cashFlow.confidence}%` }}
                                        />
                                    </div>
                                    <span className="text-white font-bold">{cashFlow.confidence}%</span>
                                </div>
                                {cashFlow.risk_indicators.overdraft_count > 0 && (
                                    <p className="text-yellow-400 text-sm mt-2">
                                        ⚠️ {cashFlow.risk_indicators.overdraft_count} overdrafts detected
                                    </p>
                                )}
                            </div>
                        </div>
                    ) : (
                        <p className="text-white/60 text-center py-4">
                            Select an account to view cash flow analysis
                        </p>
                    )}
                </div>
            )}

            {/* Data Sources Info */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Supported Data Sources</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                        { icon: '🏦', name: 'Bank Accounts', desc: 'Transaction history' },
                        { icon: '🚗', name: 'Gig Income', desc: 'Uber, Lyft, etc.' },
                        { icon: '🏠', name: 'Rent Payments', desc: 'Payment history' },
                        { icon: '💡', name: 'Utilities', desc: 'Bill payments' },
                    ].map((source, i) => (
                        <div key={i} className="bg-white/5 rounded-lg p-4 text-center">
                            <div className="text-3xl mb-2">{source.icon}</div>
                            <h3 className="text-white font-medium">{source.name}</h3>
                            <p className="text-white/50 text-sm">{source.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default AlternativeDataPage;
