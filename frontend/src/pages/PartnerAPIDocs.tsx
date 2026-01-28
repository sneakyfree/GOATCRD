import { useState } from 'react';
import { Link } from 'react-router-dom';

interface APIEndpoint {
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
    path: string;
    summary: string;
    description: string;
    requestBody?: string;
    responseExample?: string;
    parameters?: { name: string; type: string; required: boolean; description: string }[];
}

const API_ENDPOINTS: APIEndpoint[] = [
    {
        method: 'POST',
        path: '/api/v1/decisions',
        summary: 'Create Decision Request',
        description: 'Submit consumer data for credit decision. Returns decision ID for async retrieval.',
        requestBody: `{
  "consumer_id": "string",
  "income": 85000,
  "credit_score": 720,
  "employment_status": "employed",
  "debt_to_income": 0.32
}`,
        responseExample: `{
  "decision_id": "dec-abc123",
  "status": "processing",
  "estimated_completion": "2024-01-15T10:30:00Z"
}`,
        parameters: [
            { name: 'X-Partner-ID', type: 'header', required: true, description: 'Your partner API key' },
            { name: 'X-Request-ID', type: 'header', required: false, description: 'Idempotency key' },
        ]
    },
    {
        method: 'GET',
        path: '/api/v1/decisions/{decision_id}',
        summary: 'Get Decision Result',
        description: 'Retrieve the result of a previously submitted decision request.',
        responseExample: `{
  "decision_id": "dec-abc123",
  "outcome": "ELIGIBLE",
  "confidence": 0.94,
  "programs": [...],
  "reason_codes": ["R001", "R003"],
  "created_at": "2024-01-15T10:25:00Z"
}`,
        parameters: [
            { name: 'decision_id', type: 'path', required: true, description: 'The decision ID from create request' },
            { name: 'include_explanation', type: 'query', required: false, description: 'Include detailed explanation' },
        ]
    },
    {
        method: 'GET',
        path: '/api/v1/scenarios/{case_id}',
        summary: 'List Scenarios',
        description: 'Get all evaluated scenarios for a consumer case.',
        responseExample: `{
  "case_id": "case-xyz789",
  "scenarios": [
    { "program": "Standard Card", "outcome": "ELIGIBLE", "monthly_payment": 250 },
    { "program": "Premium Card", "outcome": "REFER", "reason": "DTI threshold" }
  ]
}`,
        parameters: [
            { name: 'case_id', type: 'path', required: true, description: 'The case ID' },
        ]
    },
    {
        method: 'POST',
        path: '/api/v1/webhooks/register',
        summary: 'Register Webhook',
        description: 'Register a callback URL for decision completion notifications.',
        requestBody: `{
  "url": "https://your-domain.com/webhooks/decisions",
  "events": ["decision.complete", "decision.failed"],
  "secret": "your-webhook-secret"
}`,
        responseExample: `{
  "webhook_id": "wh-123",
  "status": "active",
  "created_at": "2024-01-15T10:00:00Z"
}`
    },
    {
        method: 'GET',
        path: '/api/v1/health',
        summary: 'Health Check',
        description: 'Check API availability and current system status.',
        responseExample: `{
  "status": "healthy",
  "version": "2.3.1",
  "timestamp": "2024-01-15T10:30:00Z"
}`
    },
];

export default function PartnerAPIDocs() {
    const [selectedEndpoint, setSelectedEndpoint] = useState<APIEndpoint | null>(API_ENDPOINTS[0]);
    const [activeTab, setActiveTab] = useState<'request' | 'response'>('request');

    const getMethodColor = (method: string) => {
        switch (method) {
            case 'GET': return 'bg-green-500/20 text-green-400';
            case 'POST': return 'bg-blue-500/20 text-blue-400';
            case 'PUT': return 'bg-orange-500/20 text-orange-400';
            case 'DELETE': return 'bg-red-500/20 text-red-400';
            case 'PATCH': return 'bg-purple-500/20 text-purple-400';
            default: return 'bg-white/20 text-white/60';
        }
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                        <span className="text-4xl">📚</span>
                        Partner API Documentation
                    </h1>
                    <p className="text-white/60 mt-2">
                        Integration guide and endpoint reference for LaaS partners
                    </p>
                </div>
                <div className="flex gap-3">
                    <button className="btn-secondary">
                        📥 Download OpenAPI Spec
                    </button>
                    <Link to="/admin/partners" className="btn-secondary">
                        ← Back to Partners
                    </Link>
                </div>
            </div>

            {/* Quick Start */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Quick Start</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white/5 rounded-lg p-4">
                        <div className="text-2xl mb-2">1️⃣</div>
                        <h3 className="text-white font-medium mb-1">Get API Key</h3>
                        <p className="text-white/60 text-sm">Contact admin to receive your X-Partner-ID key</p>
                    </div>
                    <div className="bg-white/5 rounded-lg p-4">
                        <div className="text-2xl mb-2">2️⃣</div>
                        <h3 className="text-white font-medium mb-1">Configure Webhook</h3>
                        <p className="text-white/60 text-sm">Register callback URL for async notifications</p>
                    </div>
                    <div className="bg-white/5 rounded-lg p-4">
                        <div className="text-2xl mb-2">3️⃣</div>
                        <h3 className="text-white font-medium mb-1">Submit Decisions</h3>
                        <p className="text-white/60 text-sm">POST to /decisions with consumer data</p>
                    </div>
                </div>
            </div>

            {/* Base URL */}
            <div className="glass rounded-xl p-4">
                <div className="flex items-center justify-between">
                    <div>
                        <span className="text-white/60 text-sm">Base URL (Production)</span>
                        <p className="text-white font-mono">https://api.goatcrd.com/v1</p>
                    </div>
                    <div>
                        <span className="text-white/60 text-sm">Sandbox</span>
                        <p className="text-white font-mono">https://sandbox.goatcrd.com/v1</p>
                    </div>
                </div>
            </div>

            {/* Endpoints Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Endpoint List */}
                <div className="lg:col-span-1 space-y-2">
                    <h3 className="text-white/60 text-sm font-medium mb-3">ENDPOINTS</h3>
                    {API_ENDPOINTS.map((endpoint, i) => (
                        <div
                            key={i}
                            onClick={() => setSelectedEndpoint(endpoint)}
                            className={`rounded-lg p-3 cursor-pointer transition-colors ${selectedEndpoint === endpoint
                                    ? 'bg-purple-500/20 border border-purple-500'
                                    : 'bg-white/5 hover:bg-white/10 border border-transparent'
                                }`}
                        >
                            <div className="flex items-center gap-2 mb-1">
                                <span className={`px-2 py-0.5 rounded text-xs font-medium ${getMethodColor(endpoint.method)}`}>
                                    {endpoint.method}
                                </span>
                                <span className="text-white/60 font-mono text-sm truncate">{endpoint.path}</span>
                            </div>
                            <p className="text-white text-sm">{endpoint.summary}</p>
                        </div>
                    ))}
                </div>

                {/* Endpoint Detail */}
                <div className="lg:col-span-2 glass rounded-xl p-6">
                    {selectedEndpoint && (
                        <div className="space-y-6">
                            {/* Endpoint Header */}
                            <div>
                                <div className="flex items-center gap-3 mb-2">
                                    <span className={`px-3 py-1 rounded text-sm font-medium ${getMethodColor(selectedEndpoint.method)}`}>
                                        {selectedEndpoint.method}
                                    </span>
                                    <span className="text-white font-mono">{selectedEndpoint.path}</span>
                                </div>
                                <h2 className="text-xl font-semibold text-white">{selectedEndpoint.summary}</h2>
                                <p className="text-white/60 mt-2">{selectedEndpoint.description}</p>
                            </div>

                            {/* Parameters */}
                            {selectedEndpoint.parameters && selectedEndpoint.parameters.length > 0 && (
                                <div>
                                    <h3 className="text-white/80 font-medium mb-3">Parameters</h3>
                                    <div className="space-y-2">
                                        {selectedEndpoint.parameters.map((param, i) => (
                                            <div key={i} className="bg-white/5 rounded-lg p-3 flex items-start justify-between">
                                                <div>
                                                    <span className="text-white font-mono">{param.name}</span>
                                                    <span className="text-white/40 text-sm ml-2">({param.type})</span>
                                                    {param.required && (
                                                        <span className="ml-2 text-red-400 text-xs">required</span>
                                                    )}
                                                    <p className="text-white/60 text-sm mt-1">{param.description}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Request/Response Tabs */}
                            <div>
                                <div className="flex gap-2 border-b border-white/10 mb-4">
                                    <button
                                        onClick={() => setActiveTab('request')}
                                        className={`px-4 py-2 font-medium ${activeTab === 'request'
                                                ? 'text-purple-400 border-b-2 border-purple-500'
                                                : 'text-white/60 hover:text-white'
                                            }`}
                                    >
                                        Request Body
                                    </button>
                                    <button
                                        onClick={() => setActiveTab('response')}
                                        className={`px-4 py-2 font-medium ${activeTab === 'response'
                                                ? 'text-purple-400 border-b-2 border-purple-500'
                                                : 'text-white/60 hover:text-white'
                                            }`}
                                    >
                                        Response
                                    </button>
                                </div>

                                <pre className="bg-black/40 rounded-lg p-4 text-green-400 text-sm overflow-x-auto">
                                    {activeTab === 'request'
                                        ? (selectedEndpoint.requestBody || '// No request body required')
                                        : (selectedEndpoint.responseExample || '// Response format varies')
                                    }
                                </pre>
                            </div>

                            {/* Try It Button */}
                            <div className="flex gap-3">
                                <button className="btn-primary flex-1">
                                    🔧 Try in Sandbox
                                </button>
                                <button className="btn-secondary">
                                    📋 Copy cURL
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Authentication Section */}
            <div className="glass rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Authentication</h2>
                <p className="text-white/60 mb-4">
                    All API requests must include your Partner API key in the X-Partner-ID header.
                </p>
                <pre className="bg-black/40 rounded-lg p-4 text-green-400 text-sm">
                    {`curl -X POST https://api.goatcrd.com/v1/decisions \\
  -H "Content-Type: application/json" \\
  -H "X-Partner-ID: your-api-key-here" \\
  -d '{"consumer_id": "...", "income": 85000}'`}
                </pre>
            </div>
        </div>
    );
}
