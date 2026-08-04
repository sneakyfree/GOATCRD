/**
 * Frontend Error Tracking Service
 * S6.3 - Centralized error tracking and reporting
 */

interface ErrorContext {
    component?: string;
    action?: string;
    userId?: string;
    sessionId?: string;
    route?: string;
    timestamp: string;
    userAgent: string;
    screenSize: string;
    extra?: Record<string, unknown>;
}

interface TrackedError {
    id: string;
    message: string;
    stack?: string;
    type: 'error' | 'warning' | 'info';
    context: ErrorContext;
    count: number;
    firstSeen: string;
    lastSeen: string;
}

class ErrorTracker {
    private errors: Map<string, TrackedError> = new Map();
    private listeners: Array<(error: TrackedError) => void> = [];
    private readonly maxErrors = 100;
    private sessionId: string;

    constructor() {
        this.sessionId = this.generateSessionId();
        this.setupGlobalHandlers();
    }

    private generateSessionId(): string {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    private setupGlobalHandlers(): void {
        // Global error handler
        window.addEventListener('error', (event) => {
            this.captureError(event.error || new Error(event.message), {
                component: 'global',
                action: 'unhandled_error',
            });
        });

        // Unhandled promise rejection
        window.addEventListener('unhandledrejection', (event) => {
            this.captureError(
                event.reason instanceof Error
                    ? event.reason
                    : new Error(String(event.reason)),
                {
                    component: 'global',
                    action: 'unhandled_rejection',
                }
            );
        });

        // Network error detection
        window.addEventListener('offline', () => {
            this.captureWarning('Network connection lost', {
                component: 'network',
                action: 'offline',
            });
        });

        // Performance issues
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.entryType === 'longtask' && entry.duration > 100) {
                            this.captureWarning(`Long task detected: ${entry.duration}ms`, {
                                component: 'performance',
                                action: 'long_task',
                                extra: { duration: entry.duration },
                            });
                        }
                    }
                });
                observer.observe({ entryTypes: ['longtask'] });
            } catch {
                // PerformanceObserver not fully supported
            }
        }
    }

    private createContext(partial: Partial<ErrorContext> = {}): ErrorContext {
        return {
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            screenSize: `${window.innerWidth}x${window.innerHeight}`,
            route: window.location.pathname,
            sessionId: this.sessionId,
            ...partial,
        };
    }

    private generateErrorHash(error: Error, context: ErrorContext): string {
        const key = `${error.message}:${context.component}:${context.action}`;
        let hash = 0;
        for (let i = 0; i < key.length; i++) {
            const char = key.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return Math.abs(hash).toString(36);
    }

    captureError(error: Error, contextData: Partial<ErrorContext> = {}): void {
        const context = this.createContext(contextData);
        const hash = this.generateErrorHash(error, context);

        const existing = this.errors.get(hash);
        if (existing) {
            existing.count++;
            existing.lastSeen = context.timestamp;
        } else {
            const tracked: TrackedError = {
                id: hash,
                message: error.message,
                stack: error.stack,
                type: 'error',
                context,
                count: 1,
                firstSeen: context.timestamp,
                lastSeen: context.timestamp,
            };

            this.errors.set(hash, tracked);
            this.notifyListeners(tracked);

            // Prune old errors if over limit
            if (this.errors.size > this.maxErrors) {
                const oldest = Array.from(this.errors.entries())
                    .sort(([, a], [, b]) => a.lastSeen.localeCompare(b.lastSeen))[0];
                if (oldest) {
                    this.errors.delete(oldest[0]);
                }
            }
        }

        // Log to console in development
        if (import.meta.env.DEV) {
            console.error('[ErrorTracker]', error.message, context);
        }
    }

    captureWarning(message: string, contextData: Partial<ErrorContext> = {}): void {
        const error = new Error(message);
        const context = this.createContext(contextData);
        const hash = this.generateErrorHash(error, context);

        const existing = this.errors.get(hash);
        if (existing) {
            existing.count++;
            existing.lastSeen = context.timestamp;
        } else {
            const tracked: TrackedError = {
                id: hash,
                message,
                type: 'warning',
                context,
                count: 1,
                firstSeen: context.timestamp,
                lastSeen: context.timestamp,
            };

            this.errors.set(hash, tracked);
            this.notifyListeners(tracked);
        }
    }

    captureInfo(message: string, contextData: Partial<ErrorContext> = {}): void {
        const context = this.createContext(contextData);
        const tracked: TrackedError = {
            id: `info-${Date.now()}`,
            message,
            type: 'info',
            context,
            count: 1,
            firstSeen: context.timestamp,
            lastSeen: context.timestamp,
        };

        // Don't store info, just notify and log
        this.notifyListeners(tracked);

        if (import.meta.env.DEV) {
            console.info('[ErrorTracker]', message, context);
        }
    }

    private notifyListeners(error: TrackedError): void {
        for (const listener of this.listeners) {
            try {
                listener(error);
            } catch {
                // Prevent listener errors from breaking tracking
            }
        }
    }

    onError(callback: (error: TrackedError) => void): () => void {
        this.listeners.push(callback);
        return () => {
            const index = this.listeners.indexOf(callback);
            if (index > -1) {
                this.listeners.splice(index, 1);
            }
        };
    }

    getErrors(): TrackedError[] {
        return Array.from(this.errors.values())
            .sort((a, b) => b.lastSeen.localeCompare(a.lastSeen));
    }

    getErrorStats(): {
        total: number;
        byType: Record<string, number>;
        byComponent: Record<string, number>;
    } {
        const errors = this.getErrors();

        const byType: Record<string, number> = {};
        const byComponent: Record<string, number> = {};

        for (const error of errors) {
            byType[error.type] = (byType[error.type] || 0) + error.count;
            const component = error.context.component || 'unknown';
            byComponent[component] = (byComponent[component] || 0) + error.count;
        }

        return {
            total: errors.reduce((sum, e) => sum + e.count, 0),
            byType,
            byComponent,
        };
    }

    clearErrors(): void {
        this.errors.clear();
    }

    exportErrors(): string {
        return JSON.stringify(this.getErrors(), null, 2);
    }

    // API submission for backend tracking
    async submitToBackend(endpoint = '/api/v1/errors/report'): Promise<void> {
        const errors = this.getErrors();
        if (errors.length === 0) return;

        try {
            await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: this.sessionId,
                    errors,
                    stats: this.getErrorStats(),
                }),
            });
        } catch {
            // Silent fail for error reporting
        }
    }
}

// Global singleton
export const errorTracker = new ErrorTracker();

// React Error Boundary helper
export function captureComponentError(
    error: Error,
    componentStack: string,
    componentName: string
): void {
    errorTracker.captureError(error, {
        component: componentName,
        action: 'render_error',
        extra: { componentStack },
    });
}

// API error wrapper
export async function withErrorTracking<T>(
    promise: Promise<T>,
    context: Partial<ErrorContext>
): Promise<T> {
    try {
        return await promise;
    } catch (error) {
        errorTracker.captureError(
            error instanceof Error ? error : new Error(String(error)),
            { ...context, action: 'api_error' }
        );
        throw error;
    }
}

// Hook for components
export function useErrorHandler() {
    return {
        captureError: (error: Error, context?: Partial<ErrorContext>) =>
            errorTracker.captureError(error, context),
        captureWarning: (message: string, context?: Partial<ErrorContext>) =>
            errorTracker.captureWarning(message, context),
    };
}

export default errorTracker;
