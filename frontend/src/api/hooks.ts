/**
 * React hooks for API data fetching
 * Provides loading, error, and data states with automatic refetching
 */
import { useState, useEffect, useCallback } from 'react';
import api, {
    Scenario,
    ScenarioRun,
    PulseAlert,
    Consent,
    RetentionSetting,
    AccessLogEntry
} from './client';

// Generic hook for API calls
interface UseApiState<T> {
    data: T | null;
    loading: boolean;
    error: string | null;
    refetch: () => Promise<void>;
}

function useApi<T>(
    fetcher: () => Promise<T>,
    deps: unknown[] = [],
    immediate = true
): UseApiState<T> {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(immediate);
    const [error, setError] = useState<string | null>(null);

    const fetch = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await fetcher();
            setData(result);
        } catch (err) {
            setError((err as { message: string }).message || 'An error occurred');
        } finally {
            setLoading(false);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, deps);

    useEffect(() => {
        if (immediate) {
            fetch();
        }
    }, [fetch, immediate]);

    return { data, loading, error, refetch: fetch };
}

// =============================================================================
// Scenarios Hooks
// =============================================================================

export function useScenarioRuns(caseId: string | undefined) {
    return useApi<ScenarioRun[]>(
        () => caseId ? api.scenarios.listRuns(caseId) : Promise.resolve([]),
        [caseId],
        !!caseId
    );
}

export function useScenarioRun(caseId: string | undefined, runId: string | undefined) {
    return useApi(
        () => caseId && runId
            ? api.scenarios.getRun(caseId, runId)
            : Promise.reject('Missing IDs'),
        [caseId, runId],
        !!caseId && !!runId
    );
}

export function useScenarios(caseId: string | undefined, runId: string | undefined) {
    const [scenarios, setScenarios] = useState<Scenario[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!caseId || !runId) {
            setLoading(false);
            return;
        }

        setLoading(true);
        api.scenarios.getRun(caseId, runId)
            .then((result) => {
                const all = [
                    ...result.eligible,
                    ...result.refer,
                    ...result.not_eligible,
                ];
                setScenarios(all);
            })
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false));
    }, [caseId, runId]);

    return { scenarios, loading, error };
}

export function useRankedScenarios(
    caseId: string | undefined,
    runId: string | undefined,
    mode: 'best_fit' | 'lowest_payment' | 'fastest_close' | 'highest_approval' = 'best_fit'
) {
    return useApi(
        () => caseId && runId
            ? api.scenarios.getRankings(caseId, runId, mode)
            : Promise.reject('Missing IDs'),
        [caseId, runId, mode],
        !!caseId && !!runId
    );
}

// =============================================================================
// Simulation Hooks
// =============================================================================

export function useSimulation(caseId: string | undefined) {
    const [result, setResult] = useState<{
        changes_summary: string;
        confidence: number;
        status_changes: Array<{ scenario_id: string; old_status: string; new_status: string }>;
    } | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const simulate = useCallback(async (changes: Record<string, unknown>) => {
        if (!caseId) return;

        setLoading(true);
        setError(null);
        try {
            const res = await api.scenarios.simulate(caseId, changes);
            setResult(res);
        } catch (err) {
            setError((err as { message: string }).message);
        } finally {
            setLoading(false);
        }
    }, [caseId]);

    return { result, loading, error, simulate };
}

// =============================================================================
// Pulse Alerts Hooks
// =============================================================================

export function usePulseAlerts(caseId: string | undefined) {
    return useApi<PulseAlert[]>(
        () => caseId ? api.pulse.listAlerts(caseId) : Promise.resolve([]),
        [caseId],
        !!caseId
    );
}

export function usePulseSubscription(caseId: string | undefined) {
    const [subscription, setSubscription] = useState<{
        enabled: boolean;
        frequency: string;
    } | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!caseId) {
            setLoading(false);
            return;
        }

        api.pulse.getSubscription(caseId)
            .then(setSubscription)
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false));
    }, [caseId]);

    const updateSubscription = useCallback(async (enabled: boolean, frequency?: string) => {
        if (!caseId) return;

        setLoading(true);
        try {
            const result = await api.pulse.updateSubscription(caseId, enabled, frequency);
            setSubscription(result);
        } catch (err) {
            setError((err as { message: string }).message);
        } finally {
            setLoading(false);
        }
    }, [caseId]);

    return { subscription, loading, error, updateSubscription };
}

// =============================================================================
// Consents Hooks
// =============================================================================

export function useConsents(caseId: string | undefined) {
    return useApi<Consent[]>(
        () => caseId ? api.consents.list(caseId) : Promise.resolve([]),
        [caseId],
        !!caseId
    );
}

// =============================================================================
// Retention Hooks
// =============================================================================

export function useRetentionSettings(caseId: string | undefined) {
    return useApi<RetentionSetting[]>(
        () => caseId ? api.retention.getSettings(caseId) : Promise.resolve([]),
        [caseId],
        !!caseId
    );
}

// =============================================================================  
// Access Log Hooks
// =============================================================================

export function useAccessLog(caseId: string | undefined, resourceType?: string) {
    return useApi<AccessLogEntry[]>(
        () => caseId ? api.accessLog.list(caseId, 50, resourceType) : Promise.resolve([]),
        [caseId, resourceType],
        !!caseId
    );
}

// =============================================================================
// Mock Fallback Wrapper
// =============================================================================

/**
 * Wraps an API call with mock data fallback for demo resilience.
 * If the API fails, returns mock data instead of throwing.
 */
export function useMockFallback<T>(
    apiCall: () => Promise<T>,
    mockData: T,
    deps: unknown[] = []
): UseApiState<T> {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isUsingMock, setIsUsingMock] = useState(false);

    const fetch = useCallback(async () => {
        setLoading(true);
        setError(null);
        setIsUsingMock(false);

        try {
            const result = await apiCall();
            setData(result);
        } catch (err) {
            // Fallback to mock data
            console.warn('API call failed, using mock data:', (err as Error).message);
            setData(mockData);
            setIsUsingMock(true);
            setError(null); // Don't show error when using mock
        } finally {
            setLoading(false);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, deps);

    useEffect(() => {
        fetch();
    }, [fetch]);

    return {
        data,
        loading,
        error: isUsingMock ? null : error,
        refetch: fetch
    };
}

export default {
    useScenarioRuns,
    useScenarioRun,
    useScenarios,
    useRankedScenarios,
    useSimulation,
    usePulseAlerts,
    usePulseSubscription,
    useConsents,
    useRetentionSettings,
    useAccessLog,
    useMockFallback,
};
