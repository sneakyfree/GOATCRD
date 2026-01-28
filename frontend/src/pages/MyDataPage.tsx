import { Link } from 'react-router-dom';

export function MyDataPage() {

    const dataSections = [
        {
            title: 'Data Export',
            description: 'Download all your data in JSON or CSV format',
            icon: '📥',
            link: '/export',
            color: 'from-blue-500 to-cyan-500',
        },
        {
            title: 'Access Log',
            description: 'See who accessed your data, when, and why',
            icon: '📋',
            link: '/access-log',
            color: 'from-purple-500 to-pink-500',
        },
        {
            title: 'Consent Management',
            description: 'View and manage your data sharing consents',
            icon: '🔐',
            link: '/consents',
            color: 'from-green-500 to-emerald-500',
        },
        {
            title: 'Retention Settings',
            description: 'Control how long we keep your data',
            icon: '⏱️',
            link: '/retention',
            color: 'from-orange-500 to-amber-500',
        },
    ];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                    <span className="text-4xl">🔒</span>
                    My Data Rights
                </h1>
                <p className="text-white/60 mt-2">
                    You're in control. Access, export, or delete your data at any time.
                </p>
            </div>

            {/* 1033 Compliance Banner */}
            <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 rounded-xl p-6">
                <div className="flex items-start gap-4">
                    <div className="text-4xl">🏛️</div>
                    <div>
                        <h2 className="text-xl font-semibold text-white">CFPB 1033 Compliant</h2>
                        <p className="text-white/70 mt-2">
                            GOATCRD is built to comply with the Consumer Financial Protection Bureau's
                            Section 1033 requirements. You have the right to:
                        </p>
                        <ul className="mt-3 space-y-2 text-white/60">
                            <li className="flex items-center gap-2">
                                <span className="text-green-400">✓</span>
                                Access all your financial data in machine-readable format
                            </li>
                            <li className="flex items-center gap-2">
                                <span className="text-green-400">✓</span>
                                Know who accessed your data and when
                            </li>
                            <li className="flex items-center gap-2">
                                <span className="text-green-400">✓</span>
                                Revoke third-party access at any time
                            </li>
                            <li className="flex items-center gap-2">
                                <span className="text-green-400">✓</span>
                                Request deletion of your data
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Data Sections Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {dataSections.map((section, index) => (
                    <Link
                        key={index}
                        to={section.link}
                        className="glass rounded-xl p-6 hover:scale-105 transition-transform group"
                    >
                        <div className="flex items-start justify-between">
                            <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${section.color} flex items-center justify-center text-2xl`}>
                                {section.icon}
                            </div>
                            <span className="text-white/30 group-hover:text-white/60 transition-colors">→</span>
                        </div>
                        <h3 className="text-xl font-semibold text-white mt-4">{section.title}</h3>
                        <p className="text-white/60 mt-2">{section.description}</p>
                    </Link>
                ))}
            </div>

            {/* Quick Stats */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Your Data Summary</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                        { label: 'Cases', value: '3', icon: '📁' },
                        { label: 'Consents', value: '5', icon: '✅' },
                        { label: 'Exports', value: '2', icon: '📤' },
                        { label: 'Data Points', value: '47', icon: '📊' },
                    ].map((stat, i) => (
                        <div key={i} className="bg-white/5 rounded-lg p-4 text-center">
                            <span className="text-2xl">{stat.icon}</span>
                            <p className="text-2xl font-bold text-white mt-2">{stat.value}</p>
                            <p className="text-white/50 text-sm">{stat.label}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Delete My Data */}
            <div className="glass rounded-xl p-6 border border-red-500/20">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                            <span className="text-red-400">⚠️</span>
                            Delete My Data
                        </h2>
                        <p className="text-white/60 mt-1">
                            Request deletion of all your personal data. This action is irreversible.
                        </p>
                    </div>
                    <button className="bg-red-500/20 text-red-300 hover:bg-red-500/30 px-6 py-2 rounded-lg transition-colors">
                        Request Deletion
                    </button>
                </div>
                <p className="text-white/40 text-sm mt-4">
                    Deletion requests are processed within 30 days and verified across all downstream systems.
                </p>
            </div>

            {/* Contact Support */}
            <div className="text-center text-white/40 text-sm">
                <p>
                    Questions about your data rights?
                    <a href="mailto:privacy@goatcrd.com" className="text-purple-400 hover:text-purple-300 ml-1">
                        Contact our Privacy Team
                    </a>
                </p>
            </div>
        </div>
    );
}

export default MyDataPage;
