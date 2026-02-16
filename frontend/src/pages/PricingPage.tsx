/**
 * GOATCRD Pricing Page
 *
 * 3-tier subscription pricing with Stripe checkout.
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
    Check,
    Sparkles,
    Users,
    Building2,
    ArrowLeft,
    ArrowRight,
} from 'lucide-react';

interface PricingTier {
    id: string;
    name: string;
    price: number;
    description: string;
    features: string[];
    highlighted?: boolean;
    cta: string;
}

const PRICING_TIERS: PricingTier[] = [
    {
        id: 'free',
        name: 'Free',
        price: 0,
        description: 'Try GOATCRD with basic features',
        features: [
            '10 credit assessments per month',
            'Basic intake wizard',
            'Standard reason codes',
            'Email support',
        ],
        cta: 'Get Started Free',
    },
    {
        id: 'pro',
        name: 'Pro',
        price: 79,
        description: 'For growing lending operations',
        features: [
            'Unlimited assessments',
            'Full 7-agent analysis',
            'What-If simulator',
            'Alternative data integration',
            'Fairness monitoring',
            'API access',
            'Priority support',
        ],
        highlighted: true,
        cta: 'Start Pro Trial',
    },
    {
        id: 'enterprise',
        name: 'Enterprise',
        price: 299,
        description: 'For institutions at scale',
        features: [
            'Everything in Pro',
            'Multi-program management',
            'Custom rulesets engine',
            'White-label partner portal',
            'SOC2 compliance reports',
            'Dedicated success manager',
            'SLA guarantee',
        ],
        cta: 'Contact Sales',
    },
];

export default function PricingPage() {
    const [isLoading, setIsLoading] = useState(false);
    const [loadingTier, setLoadingTier] = useState<string | null>(null);

    const handleSubscribe = async (tierId: string) => {
        if (tierId === 'free') {
            window.location.href = '/intake/new';
            return;
        }

        if (tierId === 'enterprise') {
            window.location.href = 'mailto:sales@goatcrd.com?subject=Enterprise%20Inquiry';
            return;
        }

        setIsLoading(true);
        setLoadingTier(tierId);

        try {
            const response = await fetch('/api/payments/create-checkout-session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tier_id: tierId,
                    success_url: window.location.origin + '/dashboard?subscription=success',
                    cancel_url: window.location.origin + '/pricing',
                }),
            });

            const data = await response.json();

            if (data.checkout_url) {
                window.location.href = data.checkout_url;
            } else {
                alert(data.detail || 'Failed to create checkout session');
            }
        } catch (error) {
            alert('Unable to connect to payment service. Please try again.');
        } finally {
            setIsLoading(false);
            setLoadingTier(null);
        }
    };

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
                    <h1 className="text-4xl font-bold mb-4">Choose Your Plan</h1>
                    <p className="text-xl text-purple-100 max-w-2xl mx-auto">
                        Scale your credit intelligence with the right tools for your needs.
                    </p>
                </div>
            </header>

            {/* Pricing */}
            <section className="container-responsive py-12 -mt-8">
                <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                    {PRICING_TIERS.map(tier => (
                        <div
                            key={tier.id}
                            className={`relative glass-card transition-all hover:scale-[1.02] ${tier.highlighted
                                    ? 'ring-2 ring-primary-400'
                                    : ''
                                }`}
                        >
                            {tier.highlighted && (
                                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                                    <span className="inline-flex items-center gap-1 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-1 text-sm font-medium text-white">
                                        <Sparkles className="h-3.5 w-3.5" />
                                        Most Popular
                                    </span>
                                </div>
                            )}

                            <div className="text-center mb-6">
                                <div className="mb-4 mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-white/10">
                                    {tier.id === 'free' && <Building2 className="h-6 w-6 text-primary-400" />}
                                    {tier.id === 'pro' && <Sparkles className="h-6 w-6 text-primary-400" />}
                                    {tier.id === 'enterprise' && <Users className="h-6 w-6 text-primary-400" />}
                                </div>
                                <h3 className="text-xl font-bold text-white">{tier.name}</h3>
                                <p className="text-sm text-white/60 mt-1">{tier.description}</p>
                            </div>

                            <div className="text-center mb-6">
                                <span className="text-4xl font-bold text-white">
                                    ${tier.price}
                                </span>
                                <span className="text-white/60">/month</span>
                            </div>

                            <ul className="space-y-3 mb-8">
                                {tier.features.map((feature, idx) => (
                                    <li key={idx} className="flex items-start gap-3">
                                        <Check className="h-5 w-5 shrink-0 text-green-400 mt-0.5" />
                                        <span className="text-sm text-white/80">{feature}</span>
                                    </li>
                                ))}
                            </ul>

                            <button
                                onClick={() => handleSubscribe(tier.id)}
                                disabled={isLoading && loadingTier === tier.id}
                                className={`w-full flex items-center justify-center gap-2 rounded-lg py-3 px-4 font-medium transition-all ${tier.highlighted
                                        ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:shadow-lg hover:shadow-purple-500/25'
                                        : 'bg-white/10 text-white hover:bg-white/20'
                                    }`}
                            >
                                {isLoading && loadingTier === tier.id ? (
                                    <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                                ) : (
                                    <>
                                        {tier.cta}
                                        <ArrowRight className="h-4 w-4" />
                                    </>
                                )}
                            </button>
                        </div>
                    ))}
                </div>

                <p className="text-center text-sm text-white/50 mt-8">
                    All prices in USD. Cancel anytime. No hidden fees.
                </p>
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
