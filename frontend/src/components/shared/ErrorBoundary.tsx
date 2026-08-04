import { Component, ErrorInfo, ReactNode } from 'react';

interface ErrorBoundaryProps {
    children: ReactNode;
    /** Optional fallback UI */
    fallback?: ReactNode;
    /** Page name for logging */
    pageName?: string;
}

interface ErrorBoundaryState {
    hasError: boolean;
    error: Error | null;
}

/**
 * Global error boundary with branded fallback UI.
 * Wraps route-level components to prevent full app crashes.
 * Logs errors to console (connect to observability in production).
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        const page = this.props.pageName || 'unknown';
        console.error(`[GOATCRD] Error in ${page}:`, error, errorInfo);

        // TODO: Send to observability endpoint in production
        // fetch('/api/v1/metrics/error', { method: 'POST', body: JSON.stringify({ ... }) });
    }

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '50vh',
                    padding: '2rem',
                }}>
                    <div style={{
                        maxWidth: '400px',
                        textAlign: 'center',
                        background: 'rgba(255, 255, 255, 0.03)',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: '16px',
                        padding: '2.5rem',
                    }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
                        <h2 style={{
                            color: '#f1f5f9',
                            fontSize: '1.25rem',
                            marginBottom: '0.5rem',
                            fontWeight: 600,
                        }}>
                            Something went wrong
                        </h2>
                        <p style={{
                            color: '#94a3b8',
                            fontSize: '0.875rem',
                            lineHeight: 1.6,
                            marginBottom: '1.5rem',
                        }}>
                            We encountered an unexpected error. Please try refreshing the page.
                            If this persists, contact support.
                        </p>
                        <button
                            onClick={() => {
                                this.setState({ hasError: false, error: null });
                                window.location.reload();
                            }}
                            style={{
                                background: '#3b82f6',
                                color: 'white',
                                border: 'none',
                                borderRadius: '8px',
                                padding: '0.75rem 1.5rem',
                                fontSize: '0.875rem',
                                fontWeight: 600,
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                            }}
                        >
                            Refresh Page
                        </button>
                        {this.state.error && (
                            <details style={{
                                marginTop: '1.5rem',
                                textAlign: 'left',
                                color: '#64748b',
                                fontSize: '0.75rem',
                            }}>
                                <summary style={{ cursor: 'pointer', marginBottom: '0.5rem' }}>
                                    Technical Details
                                </summary>
                                <pre style={{
                                    background: 'rgba(0,0,0,0.3)',
                                    padding: '1rem',
                                    borderRadius: '8px',
                                    overflow: 'auto',
                                    maxHeight: '150px',
                                    fontSize: '0.7rem',
                                }}>
                                    {this.state.error.message}{'\n'}{this.state.error.stack}
                                </pre>
                            </details>
                        )}
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
