import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

interface IntakeChapter {
    id: number;
    name: string;
    description: string;
    completed: boolean;
}

interface IntakeData {
    [key: string]: any;
}

export function IntakePage() {
    const { caseId } = useParams();
    const navigate = useNavigate();
    const { accessToken } = useAuthStore();
    const [currentChapter, setCurrentChapter] = useState(1);
    const [intakeData, setIntakeData] = useState<IntakeData>({});
    const [isSaving, setIsSaving] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // TurboTax-style intake chapters - HARDENING R02, R30: All 10 chapters implemented
    const chapters: IntakeChapter[] = [
        { id: 1, name: 'Identity & Contact', description: 'Basic information', completed: !!intakeData.first_name },
        { id: 2, name: 'Goals', description: 'What are you looking for?', completed: !!intakeData.goal },
        { id: 3, name: 'Income & Employment', description: 'Your income sources', completed: !!intakeData.annual_income },
        { id: 4, name: 'Assets & Reserves', description: 'Savings and assets', completed: !!intakeData.total_assets },
        { id: 5, name: 'Debts & Obligations', description: 'Current debts', completed: !!intakeData.monthly_debt_payments },
        { id: 6, name: 'Credit Snapshot', description: 'Credit history overview', completed: !!intakeData.credit_score_estimate },
        { id: 7, name: 'Housing Profile', description: 'Living situation', completed: !!intakeData.housing_status },
        { id: 8, name: 'Preferences', description: 'What matters most to you', completed: !!intakeData.preferences },
        { id: 9, name: 'Consents', description: 'Data access permissions', completed: !!intakeData.consent_credit_pull },
        { id: 10, name: 'Review & Submit', description: 'Final review', completed: false },
    ];

    const updateField = (field: string, value: any) => {
        setIntakeData(prev => ({ ...prev, [field]: value }));
    };

    const saveDraft = async () => {
        if (!caseId || !accessToken) return;

        setIsSaving(true);
        try {
            await fetch(`${API_URL}/cases/${caseId}/intake/draft`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: JSON.stringify({
                    data: intakeData,
                    current_chapter: currentChapter,
                }),
            });
        } catch (error) {
            console.error('Save failed:', error);
        }
        setIsSaving(false);
    };

    const handleSubmit = async () => {
        if (!caseId || !accessToken) return;

        setIsSubmitting(true);
        try {
            await saveDraft();

            const response = await fetch(`${API_URL}/cases/${caseId}/intake/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: JSON.stringify({ confirm_review: true }),
            });

            if (response.ok) {
                navigate('/scenarios');
            }
        } catch (error) {
            console.error('Submit failed:', error);
        }
        setIsSubmitting(false);
    };

    // Auto-save on chapter change
    useEffect(() => {
        const timeout = setTimeout(() => {
            if (Object.keys(intakeData).length > 0) {
                saveDraft();
            }
        }, 1000);
        return () => clearTimeout(timeout);
    }, [currentChapter]);

    // Chapter 1: Identity & Contact
    const renderChapter1 = () => (
        <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium text-white/70 mb-2">First Name</label>
                    <input
                        type="text"
                        className="input"
                        value={intakeData.first_name || ''}
                        onChange={(e) => updateField('first_name', e.target.value)}
                        placeholder="John"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-white/70 mb-2">Last Name</label>
                    <input
                        type="text"
                        className="input"
                        value={intakeData.last_name || ''}
                        onChange={(e) => updateField('last_name', e.target.value)}
                        placeholder="Doe"
                    />
                </div>
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Email</label>
                <input
                    type="email"
                    className="input"
                    value={intakeData.email || ''}
                    onChange={(e) => updateField('email', e.target.value)}
                    placeholder="john@example.com"
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Phone</label>
                <input
                    type="tel"
                    className="input"
                    value={intakeData.phone || ''}
                    onChange={(e) => updateField('phone', e.target.value)}
                    placeholder="+1 (555) 123-4567"
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Date of Birth</label>
                <input
                    type="date"
                    className="input"
                    value={intakeData.date_of_birth || ''}
                    onChange={(e) => updateField('date_of_birth', e.target.value)}
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Last 4 of SSN</label>
                <input
                    type="text"
                    className="input w-32"
                    maxLength={4}
                    value={intakeData.ssn_last_four || ''}
                    onChange={(e) => updateField('ssn_last_four', e.target.value.replace(/\D/g, ''))}
                    placeholder="1234"
                />
                <p className="text-white/40 text-xs mt-1">Used only for identity verification</p>
            </div>
        </div>
    );

    // Chapter 2: Goals
    const renderChapter2 = () => (
        <div className="space-y-6">
            <div>
                <label className="block text-sm font-medium text-white/70 mb-3">What is your primary goal?</label>
                <div className="grid grid-cols-2 gap-3">
                    {[
                        { value: 'debt_consolidation', label: 'Consolidate Debt', icon: '💳' },
                        { value: 'major_purchase', label: 'Major Purchase', icon: '🏠' },
                        { value: 'home_improvement', label: 'Home Improvement', icon: '🔧' },
                        { value: 'emergency', label: 'Emergency Funds', icon: '🚨' },
                        { value: 'build_credit', label: 'Build Credit', icon: '📈' },
                        { value: 'other', label: 'Other', icon: '📋' },
                    ].map((option) => (
                        <button
                            key={option.value}
                            type="button"
                            onClick={() => updateField('goal', option.value)}
                            className={`p-4 rounded-lg border text-left transition-all ${intakeData.goal === option.value
                                    ? 'bg-primary-500/20 border-primary-500/50'
                                    : 'bg-white/5 border-white/10 hover:bg-white/10'
                                }`}
                        >
                            <span className="text-2xl mr-2">{option.icon}</span>
                            <span>{option.label}</span>
                        </button>
                    ))}
                </div>
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">How much do you need?</label>
                <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">$</span>
                    <input
                        type="text"
                        className="input pl-8"
                        value={intakeData.loan_amount_requested || ''}
                        onChange={(e) => updateField('loan_amount_requested', parseInt(e.target.value.replace(/\D/g, '')) || 0)}
                        placeholder="15,000"
                    />
                </div>
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">When do you need it?</label>
                <select
                    className="input"
                    value={intakeData.urgency || ''}
                    onChange={(e) => updateField('urgency', e.target.value)}
                >
                    <option value="">Select...</option>
                    <option value="asap">As soon as possible</option>
                    <option value="1_week">Within 1 week</option>
                    <option value="1_month">Within 1 month</option>
                    <option value="no_rush">No rush, exploring options</option>
                </select>
            </div>
        </div>
    );

    // Chapter 3: Income & Employment
    const renderChapter3 = () => (
        <div className="space-y-6">
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Employment Status</label>
                <select
                    className="input"
                    value={intakeData.employment_status || ''}
                    onChange={(e) => updateField('employment_status', e.target.value)}
                >
                    <option value="">Select...</option>
                    <option value="employed">Employed Full-Time</option>
                    <option value="part_time">Employed Part-Time</option>
                    <option value="self_employed">Self-Employed</option>
                    <option value="retired">Retired</option>
                    <option value="unemployed">Unemployed</option>
                </select>
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Annual Income (Gross)</label>
                <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">$</span>
                    <input
                        type="text"
                        className="input pl-8"
                        value={intakeData.annual_income || ''}
                        onChange={(e) => updateField('annual_income', parseInt(e.target.value.replace(/\D/g, '')) || 0)}
                        placeholder="72,000"
                    />
                </div>
                <p className="text-white/40 text-xs mt-1">Self-reported. Verify later for better rates.</p>
            </div>
            {intakeData.employment_status && !['unemployed', 'retired'].includes(intakeData.employment_status) && (
                <>
                    <div>
                        <label className="block text-sm font-medium text-white/70 mb-2">Employer Name</label>
                        <input
                            type="text"
                            className="input"
                            value={intakeData.employer_name || ''}
                            onChange={(e) => updateField('employer_name', e.target.value)}
                            placeholder="TechCorp Inc"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-white/70 mb-2">How long at this job?</label>
                        <select
                            className="input"
                            value={intakeData.employment_months || ''}
                            onChange={(e) => updateField('employment_months', parseInt(e.target.value))}
                        >
                            <option value="">Select...</option>
                            <option value="3">Less than 6 months</option>
                            <option value="12">6-12 months</option>
                            <option value="24">1-2 years</option>
                            <option value="36">2-5 years</option>
                            <option value="60">5+ years</option>
                        </select>
                    </div>
                </>
            )}
        </div>
    );

    // Chapter 4: Assets & Reserves
    const renderChapter4 = () => (
        <div className="space-y-6">
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Total Savings & Checking</label>
                <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">$</span>
                    <input
                        type="text"
                        className="input pl-8"
                        value={intakeData.total_liquid_assets || ''}
                        onChange={(e) => updateField('total_liquid_assets', parseInt(e.target.value.replace(/\D/g, '')) || 0)}
                        placeholder="25,000"
                    />
                </div>
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Retirement Accounts (401k, IRA)</label>
                <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">$</span>
                    <input
                        type="text"
                        className="input pl-8"
                        value={intakeData.retirement_assets || ''}
                        onChange={(e) => updateField('retirement_assets', parseInt(e.target.value.replace(/\D/g, '')) || 0)}
                        placeholder="50,000"
                    />
                </div>
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Other Assets</label>
                <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">$</span>
                    <input
                        type="text"
                        className="input pl-8"
                        value={intakeData.other_assets || ''}
                        onChange={(e) => updateField('other_assets', parseInt(e.target.value.replace(/\D/g, '')) || 0)}
                        placeholder="10,000"
                    />
                </div>
                <p className="text-white/40 text-xs mt-1">Vehicles, investments, property equity, etc.</p>
            </div>
        </div>
    );

    // Chapter 5: Debts & Obligations
    const renderChapter5 = () => (
        <div className="space-y-6">
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Total Monthly Debt Payments</label>
                <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">$</span>
                    <input
                        type="text"
                        className="input pl-8"
                        value={intakeData.monthly_debt_payments || ''}
                        onChange={(e) => updateField('monthly_debt_payments', parseInt(e.target.value.replace(/\D/g, '')) || 0)}
                        placeholder="800"
                    />
                </div>
                <p className="text-white/40 text-xs mt-1">Include credit cards, auto loans, student loans, etc.</p>
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Credit Card Balances (Total)</label>
                <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">$</span>
                    <input
                        type="text"
                        className="input pl-8"
                        value={intakeData.credit_card_balance || ''}
                        onChange={(e) => updateField('credit_card_balance', parseInt(e.target.value.replace(/\D/g, '')) || 0)}
                        placeholder="5,000"
                    />
                </div>
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-3">Do you have any of these?</label>
                <div className="space-y-2">
                    {[
                        { field: 'has_auto_loan', label: 'Auto Loan' },
                        { field: 'has_student_loans', label: 'Student Loans' },
                        { field: 'has_mortgage', label: 'Mortgage' },
                        { field: 'has_collections', label: 'Accounts in Collections' },
                    ].map((item) => (
                        <label key={item.field} className="flex items-center gap-3 p-3 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10">
                            <input
                                type="checkbox"
                                checked={intakeData[item.field] || false}
                                onChange={(e) => updateField(item.field, e.target.checked)}
                                className="rounded"
                            />
                            <span>{item.label}</span>
                        </label>
                    ))}
                </div>
            </div>
        </div>
    );

    // Chapter 6: Credit Snapshot
    const renderChapter6 = () => (
        <div className="space-y-6">
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Estimated Credit Score</label>
                <select
                    className="input"
                    value={intakeData.credit_score_estimate || ''}
                    onChange={(e) => updateField('credit_score_estimate', parseInt(e.target.value))}
                >
                    <option value="">Select range...</option>
                    <option value="800">800+ (Excellent)</option>
                    <option value="750">750-799 (Very Good)</option>
                    <option value="700">700-749 (Good)</option>
                    <option value="650">650-699 (Fair)</option>
                    <option value="600">600-649 (Poor)</option>
                    <option value="550">Below 600 (Very Poor)</option>
                    <option value="0">I don't know</option>
                </select>
                <p className="text-white/40 text-xs mt-1">We'll verify with your permission</p>
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-3">Recent credit events (past 2 years)</label>
                <div className="space-y-2">
                    {[
                        { field: 'recent_late_payments', label: 'Late Payments (30+ days)' },
                        { field: 'recent_hard_inquiries', label: 'Hard Credit Inquiries' },
                        { field: 'recent_new_accounts', label: 'New Credit Accounts Opened' },
                        { field: 'recent_bankruptcy', label: 'Bankruptcy Filed' },
                    ].map((item) => (
                        <label key={item.field} className="flex items-center gap-3 p-3 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10">
                            <input
                                type="checkbox"
                                checked={intakeData[item.field] || false}
                                onChange={(e) => updateField(item.field, e.target.checked)}
                                className="rounded"
                            />
                            <span>{item.label}</span>
                        </label>
                    ))}
                </div>
            </div>
        </div>
    );

    // Chapter 7: Housing Profile
    const renderChapter7 = () => (
        <div className="space-y-6">
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Housing Status</label>
                <select
                    className="input"
                    value={intakeData.housing_status || ''}
                    onChange={(e) => updateField('housing_status', e.target.value)}
                >
                    <option value="">Select...</option>
                    <option value="own_with_mortgage">Own (with mortgage)</option>
                    <option value="own_free_clear">Own (free and clear)</option>
                    <option value="rent">Rent</option>
                    <option value="living_with_family">Living with family</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Monthly Housing Payment</label>
                <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">$</span>
                    <input
                        type="text"
                        className="input pl-8"
                        value={intakeData.monthly_housing_payment || ''}
                        onChange={(e) => updateField('monthly_housing_payment', parseInt(e.target.value.replace(/\D/g, '')) || 0)}
                        placeholder="1,800"
                    />
                </div>
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Years at Current Address</label>
                <select
                    className="input"
                    value={intakeData.years_at_address || ''}
                    onChange={(e) => updateField('years_at_address', parseInt(e.target.value))}
                >
                    <option value="">Select...</option>
                    <option value="0">Less than 1 year</option>
                    <option value="2">1-2 years</option>
                    <option value="5">3-5 years</option>
                    <option value="10">5+ years</option>
                </select>
            </div>
        </div>
    );

    // Chapter 8: Preferences
    const renderChapter8 = () => (
        <div className="space-y-6">
            <div>
                <label className="block text-sm font-medium text-white/70 mb-3">What's most important to you?</label>
                <div className="space-y-2">
                    {[
                        { value: 'lowest_rate', label: 'Lowest interest rate', icon: '📉' },
                        { value: 'lowest_payment', label: 'Lowest monthly payment', icon: '💰' },
                        { value: 'fast_funding', label: 'Fastest funding', icon: '⚡' },
                        { value: 'no_fees', label: 'No origination fees', icon: '🚫' },
                        { value: 'flexible_terms', label: 'Flexible repayment', icon: '🔄' },
                    ].map((option) => (
                        <label
                            key={option.value}
                            className={`flex items-center gap-3 p-4 rounded-lg border cursor-pointer transition-all ${intakeData.primary_preference === option.value
                                    ? 'bg-primary-500/20 border-primary-500/50'
                                    : 'bg-white/5 border-white/10 hover:bg-white/10'
                                }`}
                        >
                            <input
                                type="radio"
                                name="preference"
                                checked={intakeData.primary_preference === option.value}
                                onChange={() => updateField('primary_preference', option.value)}
                                className="sr-only"
                            />
                            <span className="text-xl">{option.icon}</span>
                            <span>{option.label}</span>
                        </label>
                    ))}
                </div>
            </div>
            <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Preferred loan term</label>
                <select
                    className="input"
                    value={intakeData.preferred_term_months || ''}
                    onChange={(e) => updateField('preferred_term_months', parseInt(e.target.value))}
                >
                    <option value="">No preference</option>
                    <option value="12">12 months</option>
                    <option value="24">24 months</option>
                    <option value="36">36 months</option>
                    <option value="48">48 months</option>
                    <option value="60">60 months</option>
                </select>
            </div>
        </div>
    );

    // Chapter 9: Consents
    const renderChapter9 = () => (
        <div className="space-y-6">
            <div className="glass-card p-4 bg-sky-500/10 border-sky-500/20 mb-6">
                <p className="text-sm text-white/80">
                    <strong>Your Rights:</strong> Under Section 1033, you control your data.
                    You can revoke any consent at any time.
                </p>
            </div>
            <div className="space-y-4">
                <label className="flex items-start gap-3 p-4 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10">
                    <input
                        type="checkbox"
                        checked={intakeData.consent_credit_pull || false}
                        onChange={(e) => updateField('consent_credit_pull', e.target.checked)}
                        className="mt-1 rounded"
                    />
                    <div>
                        <span className="font-medium">Credit Report Pull</span>
                        <p className="text-sm text-white/60 mt-1">
                            Allow us to pull your credit report to provide accurate options. This is a soft pull and won't affect your score.
                        </p>
                    </div>
                </label>
                <label className="flex items-start gap-3 p-4 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10">
                    <input
                        type="checkbox"
                        checked={intakeData.consent_income_verify || false}
                        onChange={(e) => updateField('consent_income_verify', e.target.checked)}
                        className="mt-1 rounded"
                    />
                    <div>
                        <span className="font-medium">Income Verification</span>
                        <p className="text-sm text-white/60 mt-1">
                            Connect to payroll or banking providers to verify income for better rates.
                        </p>
                    </div>
                </label>
                <label className="flex items-start gap-3 p-4 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10">
                    <input
                        type="checkbox"
                        checked={intakeData.consent_terms || false}
                        onChange={(e) => updateField('consent_terms', e.target.checked)}
                        className="mt-1 rounded"
                    />
                    <div>
                        <span className="font-medium">Terms & Conditions</span>
                        <p className="text-sm text-white/60 mt-1">
                            I agree to the Terms of Service and Privacy Policy.
                        </p>
                    </div>
                </label>
            </div>
        </div>
    );

    // Chapter 10: Review & Submit
    const renderChapter10 = () => {
        const progress = chapters.filter(c => c.completed).length;

        return (
            <div className="space-y-6">
                <div className="glass-card p-6 bg-emerald-500/10 border-emerald-500/20">
                    <h3 className="text-lg font-semibold text-emerald-400 mb-2">
                        {progress >= 7 ? '✅ Ready to Submit!' : '⚠️ Almost There'}
                    </h3>
                    <p className="text-white/80">
                        You've completed {progress} of 9 sections.
                        {progress < 7 && ' Complete at least 7 sections for best results.'}
                    </p>
                </div>

                <div className="space-y-3">
                    <h4 className="font-medium text-white/80">Summary</h4>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                        <div className="bg-white/5 p-3 rounded-lg">
                            <span className="text-white/60">Requested Amount</span>
                            <p className="text-lg font-semibold">${(intakeData.loan_amount_requested || 0).toLocaleString()}</p>
                        </div>
                        <div className="bg-white/5 p-3 rounded-lg">
                            <span className="text-white/60">Annual Income</span>
                            <p className="text-lg font-semibold">${(intakeData.annual_income || 0).toLocaleString()}</p>
                        </div>
                        <div className="bg-white/5 p-3 rounded-lg">
                            <span className="text-white/60">Credit Score</span>
                            <p className="text-lg font-semibold">{intakeData.credit_score_estimate || 'Not provided'}</p>
                        </div>
                        <div className="bg-white/5 p-3 rounded-lg">
                            <span className="text-white/60">Goal</span>
                            <p className="text-lg font-semibold capitalize">{(intakeData.goal || '').replace('_', ' ') || 'Not specified'}</p>
                        </div>
                    </div>
                </div>

                <div className="pt-4">
                    <label className="flex items-start gap-3 p-4 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10">
                        <input
                            type="checkbox"
                            checked={intakeData.confirm_accuracy || false}
                            onChange={(e) => updateField('confirm_accuracy', e.target.checked)}
                            className="mt-1 rounded"
                        />
                        <div>
                            <span className="font-medium">I confirm this information is accurate</span>
                            <p className="text-sm text-white/60 mt-1">
                                I understand that providing inaccurate information may affect my eligibility.
                            </p>
                        </div>
                    </label>
                </div>
            </div>
        );
    };

    const renderCurrentChapter = () => {
        switch (currentChapter) {
            case 1: return renderChapter1();
            case 2: return renderChapter2();
            case 3: return renderChapter3();
            case 4: return renderChapter4();
            case 5: return renderChapter5();
            case 6: return renderChapter6();
            case 7: return renderChapter7();
            case 8: return renderChapter8();
            case 9: return renderChapter9();
            case 10: return renderChapter10();
            default: return null;
        }
    };

    return (
        <div className="py-8">
            <div className="flex gap-8">
                {/* Sidebar - Chapter Navigation */}
                <div className="w-64 flex-shrink-0">
                    <div className="glass-card sticky top-8 p-4">
                        <h2 className="font-semibold mb-4">Intake Progress</h2>
                        <div className="space-y-2">
                            {chapters.map((chapter) => (
                                <button
                                    key={chapter.id}
                                    onClick={() => setCurrentChapter(chapter.id)}
                                    className={`w-full text-left px-3 py-2 rounded-lg transition-all flex items-center gap-2 ${currentChapter === chapter.id
                                        ? 'bg-primary-500/20 text-primary-400'
                                        : chapter.completed
                                            ? 'text-white/70 hover:bg-white/5'
                                            : 'text-white/40'
                                        }`}
                                >
                                    <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${chapter.completed ? 'bg-green-500' : 'bg-white/20'
                                        }`}>
                                        {chapter.completed ? '✓' : chapter.id}
                                    </span>
                                    <span className="text-sm">{chapter.name}</span>
                                </button>
                            ))}
                        </div>
                        {isSaving && (
                            <p className="text-xs text-white/40 mt-4 text-center">Saving...</p>
                        )}
                    </div>
                </div>

                {/* Main Content */}
                <div className="flex-1">
                    <div className="glass-card p-6">
                        <div className="mb-6">
                            <h1 className="text-2xl font-bold mb-2">
                                {chapters[currentChapter - 1]?.name}
                            </h1>
                            <p className="text-white/70">
                                {chapters[currentChapter - 1]?.description}
                            </p>
                        </div>

                        {renderCurrentChapter()}

                        {/* Navigation */}
                        <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/10">
                            <button
                                onClick={() => setCurrentChapter(Math.max(1, currentChapter - 1))}
                                disabled={currentChapter === 1}
                                className="btn-secondary disabled:opacity-50"
                            >
                                ← Previous
                            </button>

                            <span className="text-white/50 text-sm">
                                Step {currentChapter} of {chapters.length}
                            </span>

                            {currentChapter === chapters.length ? (
                                <button
                                    onClick={handleSubmit}
                                    disabled={isSubmitting || !intakeData.confirm_accuracy || !intakeData.consent_terms}
                                    className="btn-primary disabled:opacity-50"
                                >
                                    {isSubmitting ? 'Submitting...' : 'Submit & See Options'}
                                </button>
                            ) : (
                                <button
                                    onClick={() => setCurrentChapter(currentChapter + 1)}
                                    className="btn-primary"
                                >
                                    Next →
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
