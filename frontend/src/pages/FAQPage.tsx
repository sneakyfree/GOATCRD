/**
 * GOATCRD FAQ Page
 *
 * Consumer credit FAQ with 6 categories and real-time search.
 */

import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
    Search,
    ChevronDown,
    Zap,
    FileText,
    TrendingUp,
    Database,
    Shield,
    Settings,
    ArrowLeft,
} from 'lucide-react';

interface FAQ {
    question: string;
    answer: string;
}

interface FAQCategory {
    id: string;
    title: string;
    icon: React.ReactNode;
    color: string;
    faqs: FAQ[];
}

const FAQ_CATEGORIES: FAQCategory[] = [
    {
        id: 'getting-started',
        title: 'Getting Started',
        icon: <Zap className="h-5 w-5" />,
        color: 'from-blue-500 to-cyan-400',
        faqs: [
            {
                question: 'What is GOATCRD?',
                answer: 'GOATCRD is an AI-powered consumer credit intelligence platform that provides comprehensive credit analysis, scenario modeling, and decision support using our 7-agent coordinator crew.'
            },
            {
                question: 'Who should use GOATCRD?',
                answer: 'Financial institutions, credit unions, lenders, and fintech companies that need fair, explainable, and auditable credit decisioning at scale.'
            },
            {
                question: 'How does the 7-agent crew work?',
                answer: 'Our specialized agents handle different aspects: Orchestrator, DataCollector, RiskAnalyzer, ComplianceChecker, ScenarioGenerator, ExplainabilityEngine, and AuditLogger. They work together to provide comprehensive credit analysis.'
            },
            {
                question: 'Is GOATCRD compliant with fair lending laws?',
                answer: 'Yes! We include built-in fairness monitoring, disparate impact analysis, and full audit trails to support ECOA, FCRA, and state fair lending requirements.'
            },
        ],
    },
    {
        id: 'credit-intake',
        title: 'Credit Intake',
        icon: <FileText className="h-5 w-5" />,
        color: 'from-purple-500 to-pink-500',
        faqs: [
            {
                question: 'What information is collected during intake?',
                answer: 'Standard credit application data: income, employment, existing debts, requested amount, and purpose. We also integrate with bureau data and alternative data sources when configured.'
            },
            {
                question: 'Can applicants save and resume their application?',
                answer: 'Yes! Our TurboTax-style intake supports save/resume functionality. Applicants can complete the process across multiple sessions without losing data.'
            },
            {
                question: 'How does alternative data integration work?',
                answer: 'We can incorporate rent payments, utility bills, bank transaction history, and other alternative signals to help thin-file or credit-invisible applicants demonstrate creditworthiness.'
            },
            {
                question: 'What happens after intake is complete?',
                answer: 'The application moves to our 7-agent analysis pipeline, generating eligibility determination, reason codes, and explainability narratives within seconds.'
            },
        ],
    },
    {
        id: 'score-factors',
        title: 'Score Factors',
        icon: <TrendingUp className="h-5 w-5" />,
        color: 'from-green-500 to-emerald-400',
        faqs: [
            {
                question: 'What factors influence the credit decision?',
                answer: 'Key factors include payment history, debt-to-income ratio, length of credit history, credit utilization, recent inquiries, and program-specific criteria defined in your rulesets.'
            },
            {
                question: 'How are reason codes generated?',
                answer: 'Our ExplainabilityEngine generates plain-English reason codes that explain the top factors influencing each decision, meeting adverse action notice requirements.'
            },
            {
                question: 'Can I customize scoring weights?',
                answer: 'Yes! Admins can configure rulesets with custom weights, thresholds, and criteria for different lending programs through our Admin Governance dashboard.'
            },
            {
                question: 'How do I improve my credit decision rate?',
                answer: 'Use the What-If Simulator to model different scenarios. Adjust income, debt payoff, or waiting periods to see how changes affect eligibility.'
            },
        ],
    },
    {
        id: 'alternative-data',
        title: 'Alternative Data',
        icon: <Database className="h-5 w-5" />,
        color: 'from-orange-500 to-amber-400',
        faqs: [
            {
                question: 'What alternative data sources are supported?',
                answer: 'We support rent payment history, utility payments, bank transaction analysis, employment verification, and custom data sources via our Partner API.'
            },
            {
                question: 'How does alternative data affect credit decisions?',
                answer: 'Alternative data can provide positive signals for thin-file applicants, potentially moving them from "Not Eligible" to "Refer" or even "Eligible" status.'
            },
            {
                question: 'Is alternative data use compliant with regulations?',
                answer: 'Yes! We ensure all alternative data use complies with FCRA, ECOA, and state regulations. Data is permissioned and audited end-to-end.'
            },
            {
                question: 'Can applicants see what alternative data was used?',
                answer: 'Absolutely. Our Consumer Data Rights portal allows applicants to view, correct, and manage all data used in their credit assessment.'
            },
        ],
    },
    {
        id: 'dispute-resolution',
        title: 'Dispute Resolution',
        icon: <Shield className="h-5 w-5" />,
        color: 'from-red-500 to-rose-400',
        faqs: [
            {
                question: 'How do I dispute a credit decision?',
                answer: 'Use the Access Log and Audit Viewer to review the decision details, then submit a dispute through the Consumer Portal or contact your lender directly.'
            },
            {
                question: 'What information is provided in adverse action notices?',
                answer: 'Notices include the specific reason codes, the data sources used, your right to request the credit report, and instructions for disputing inaccurate information.'
            },
            {
                question: 'How long does dispute resolution take?',
                answer: 'Initial review typically completes within 30 days per FCRA requirements. Complex cases involving data correction may take additional time.'
            },
            {
                question: 'Can I request a manual review?',
                answer: 'Yes! Our HITL (Human-in-the-Loop) review queue allows cases to be escalated for manual underwriter review when automated decisions require human judgment.'
            },
        ],
    },
    {
        id: 'platform-usage',
        title: 'Platform Usage',
        icon: <Settings className="h-5 w-5" />,
        color: 'from-slate-500 to-gray-400',
        faqs: [
            {
                question: 'How do I access the Admin Dashboard?',
                answer: 'Navigate to /admin after logging in with an admin account. From there you can manage programs, rulesets, reason codes, and partner configurations.'
            },
            {
                question: 'What does the Fairness Dashboard show?',
                answer: 'Real-time metrics on approval rates by protected class, disparate impact ratios, and alerts when fairness thresholds are exceeded.'
            },
            {
                question: 'How do confidence scores work?',
                answer: 'Each decision includes a confidence score (0-100%) indicating how certain the model is. Lower confidence cases may be flagged for human review.'
            },
            {
                question: 'Is my data secure?',
                answer: 'Yes! GOATCRD uses encryption at rest and in transit, SOC2-aligned practices, role-based access control, and comprehensive audit logging.'
            },
        ],
    },
];

function FAQItem({ faq, isOpen, onToggle }: { faq: FAQ; isOpen: boolean; onToggle: () => void }) {
    return (
        <div className="border-b border-white/10 last:border-b-0">
            <button
                onClick={onToggle}
                className="flex w-full items-center justify-between py-4 text-left transition-colors hover:text-primary-400"
            >
                <span className="font-medium text-white pr-4">{faq.question}</span>
                <ChevronDown
                    className={`h-5 w-5 shrink-0 text-white/50 transition-transform duration-200 ${isOpen ? 'rotate-180 text-primary-400' : ''
                        }`}
                />
            </button>
            <div
                className={`grid transition-all duration-200 ease-in-out ${isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
                    }`}
            >
                <div className="overflow-hidden">
                    <p className="pb-4 text-white/70 leading-relaxed">{faq.answer}</p>
                </div>
            </div>
        </div>
    );
}

export default function FAQPage() {
    const [searchQuery, setSearchQuery] = useState('');
    const [openItems, setOpenItems] = useState<Set<string>>(new Set());

    const toggleItem = (id: string) => {
        setOpenItems(prev => {
            const newSet = new Set(prev);
            if (newSet.has(id)) {
                newSet.delete(id);
            } else {
                newSet.add(id);
            }
            return newSet;
        });
    };

    const filteredCategories = useMemo(() => {
        if (!searchQuery.trim()) return FAQ_CATEGORIES;

        const query = searchQuery.toLowerCase();
        return FAQ_CATEGORIES.map(category => ({
            ...category,
            faqs: category.faqs.filter(
                faq =>
                    faq.question.toLowerCase().includes(query) ||
                    faq.answer.toLowerCase().includes(query)
            ),
        })).filter(category => category.faqs.length > 0);
    }, [searchQuery]);

    const filteredCount = filteredCategories.reduce((acc, cat) => acc + cat.faqs.length, 0);

    return (
        <div className="min-h-screen">
            {/* Hero */}
            <header className="bg-gradient-to-br from-purple-600 to-pink-600 text-white">
                <nav className="container-responsive py-4">
                    <Link
                        to="/"
                        className="inline-flex items-center gap-2 text-purple-100 hover:text-white transition-colors"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Back to Home
                    </Link>
                </nav>
                <div className="container-responsive pb-16 pt-8 text-center">
                    <h1 className="text-4xl font-bold mb-4">Frequently Asked Questions</h1>
                    <p className="text-xl text-purple-100 max-w-2xl mx-auto">
                        Everything you need to know about consumer credit intelligence,
                        fair lending, and getting the best results from GOATCRD.
                    </p>
                </div>
            </header>

            {/* Search */}
            <div className="container-responsive -mt-6">
                <div className="relative max-w-2xl mx-auto">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-white/40" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search questions..."
                        className="w-full rounded-xl border border-white/20 bg-gray-900/90 backdrop-blur-lg py-4 pl-12 pr-4 text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-xl"
                    />
                    {searchQuery && (
                        <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm text-white/50">
                            {filteredCount} results
                        </span>
                    )}
                </div>
            </div>

            {/* Categories */}
            <main className="container-responsive py-12">
                {filteredCount === 0 ? (
                    <div className="text-center py-16">
                        <h3 className="text-xl font-semibold text-white mb-2">
                            No questions found
                        </h3>
                        <p className="text-white/60">
                            Try a different search term or browse the categories below.
                        </p>
                    </div>
                ) : (
                    <div className="space-y-8">
                        {filteredCategories.map(category => (
                            <div key={category.id} className="glass-card">
                                <div className="flex items-center gap-3 mb-6">
                                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br ${category.color} text-white`}>
                                        {category.icon}
                                    </div>
                                    <h2 className="text-xl font-semibold text-white">
                                        {category.title}
                                    </h2>
                                    <span className="ml-auto text-sm text-white/50">
                                        {category.faqs.length} questions
                                    </span>
                                </div>
                                <div className="divide-y divide-white/10">
                                    {category.faqs.map((faq, idx) => (
                                        <FAQItem
                                            key={idx}
                                            faq={faq}
                                            isOpen={openItems.has(`${category.id}-${idx}`)}
                                            onToggle={() => toggleItem(`${category.id}-${idx}`)}
                                        />
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </main>

            {/* CTA */}
            <section className="bg-gradient-to-r from-purple-600 to-pink-600 text-white py-12">
                <div className="container-responsive text-center">
                    <h2 className="text-2xl font-bold mb-4">Still have questions?</h2>
                    <p className="text-purple-100 mb-6">
                        Our AI agent is available 24/7 to help with your credit questions.
                    </p>
                    <Link
                        to="/intake/new"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-purple-50 transition-colors"
                    >
                        Start New Application
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-white/40 py-8 border-t border-white/10">
                <div className="container-responsive text-center">
                    <p>&copy; 2026 GOATCRD. Consumer Credit Intelligence Platform.</p>
                </div>
            </footer>
        </div>
    );
}
