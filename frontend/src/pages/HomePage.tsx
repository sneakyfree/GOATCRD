import { Link } from 'react-router-dom';

export function HomePage() {
    return (
        <div className="py-12">
            {/* Hero Section */}
            <div className="text-center mb-16">
                <h1 className="text-5xl md:text-6xl font-bold mb-6">
                    <span className="gradient-text">Intelligent Credit Decisioning</span>
                </h1>
                <p className="text-xl text-white/70 max-w-3xl mx-auto mb-8">
                    GOATCRD is an agentic, compliance-first consumer credit intelligence platform.
                    Generate scenario universes, understand your options, and make informed decisions.
                </p>
                <div className="flex items-center justify-center gap-4">
                    <Link to="/login" className="btn-primary text-lg px-8 py-3">
                        Get Started
                    </Link>
                    <a href="#features" className="btn-secondary text-lg px-8 py-3">
                        Learn More
                    </a>
                </div>
            </div>

            {/* Features Grid */}
            <div id="features" className="grid md:grid-cols-3 gap-8 mb-16">
                <div className="glass-card">
                    <div className="text-4xl mb-4">🎯</div>
                    <h3 className="text-xl font-semibold mb-2">Scenario Universe</h3>
                    <p className="text-white/70">
                        See all your options across configured programs. Never miss an opportunity.
                    </p>
                </div>
                <div className="glass-card">
                    <div className="text-4xl mb-4">🔍</div>
                    <h3 className="text-xl font-semibold mb-2">Full Transparency</h3>
                    <p className="text-white/70">
                        Understand exactly why you qualify or don't. Clear reason codes and actionable next steps.
                    </p>
                </div>
                <div className="glass-card">
                    <div className="text-4xl mb-4">🔒</div>
                    <h3 className="text-xl font-semibold mb-2">Compliance-First</h3>
                    <p className="text-white/70">
                        Built for CFPB/ECOA/UDAP compliance. Your data rights protected by design.
                    </p>
                </div>
            </div>

            {/* What-If Section */}
            <div className="glass-card text-center mb-16">
                <h2 className="text-3xl font-bold mb-4">What If?</h2>
                <p className="text-white/70 max-w-2xl mx-auto mb-6">
                    Simulate changes before you make them. See how paying down debt or improving credit
                    could unlock new options—without any commitment.
                </p>
                <Link to="/login" className="btn-primary">
                    Try the Simulator
                </Link>
            </div>

            {/* Trust Indicators */}
            <div className="text-center">
                <p className="text-white/50 text-sm mb-4">Built with</p>
                <div className="flex items-center justify-center gap-8 text-white/40">
                    <span>🏛️ Regulator-Grade Audit</span>
                    <span>📊 Source-Labeled Data</span>
                    <span>🔐 1033-Native Privacy</span>
                </div>
            </div>
        </div>
    );
}
