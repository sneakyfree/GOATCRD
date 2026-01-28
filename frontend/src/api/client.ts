/**
 * GOATCRD API Client
 * 
 * Centralized API client for backend communication.
 * Replaces mock data with real API calls.
 */
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';

// API base URL - uses environment variable or defaults to local
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Types for API responses
export interface ApiError {
    message: string;
    code?: string;
    details?: Record<string, unknown>;
}

export interface ApiResponse<T> {
    data: T;
    success: boolean;
    error?: ApiError;
}

// Create axios instance with defaults
const apiClient: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Auth token storage
let authToken: string | null = null;

export function setAuthToken(token: string | null) {
    authToken = token;
    if (token) {
        localStorage.setItem('goatcrd_token', token);
    } else {
        localStorage.removeItem('goatcrd_token');
    }
}

export function getAuthToken(): string | null {
    if (!authToken) {
        authToken = localStorage.getItem('goatcrd_token');
    }
    return authToken;
}

// Request interceptor - add auth token
apiClient.interceptors.request.use(
    (config) => {
        const token = getAuthToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor - handle errors
apiClient.interceptors.response.use(
    (response) => response,
    (error: AxiosError<ApiError>) => {
        if (error.response?.status === 401) {
            // Clear token and redirect to login
            setAuthToken(null);
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// =============================================================================
// API Methods
// =============================================================================

// Generic request helper
async function request<T>(config: AxiosRequestConfig): Promise<T> {
    try {
        const response = await apiClient.request<T>(config);
        return response.data;
    } catch (error) {
        const axiosError = error as AxiosError<ApiError>;
        throw {
            message: axiosError.response?.data?.message || axiosError.message,
            code: axiosError.response?.status?.toString(),
            details: axiosError.response?.data?.details,
        };
    }
}

// =============================================================================
// Auth API
// =============================================================================
export const auth = {
    login: (email: string, password: string) =>
        request<{ access_token: string; token_type: string; user: unknown }>({
            method: 'POST',
            url: '/auth/login',
            data: { email, password },
        }),

    register: (data: { email: string; password: string; full_name: string }) =>
        request<{ id: string; email: string }>({
            method: 'POST',
            url: '/auth/register',
            data,
        }),

    me: () =>
        request<{ id: string; email: string; role: string }>({
            method: 'GET',
            url: '/auth/me',
        }),

    logout: () => {
        setAuthToken(null);
        return Promise.resolve();
    },
};

// =============================================================================
// Cases API
// =============================================================================
export interface Case {
    id: string;
    consumer_id: string;
    external_reference?: string;
    status: string;
    created_at: string;
    updated_at: string;
}

export const cases = {
    list: (limit = 20, offset = 0) =>
        request<Case[]>({
            method: 'GET',
            url: '/cases',
            params: { limit, offset },
        }),

    get: (caseId: string) =>
        request<Case>({
            method: 'GET',
            url: `/cases/${caseId}`,
        }),

    create: (externalReference?: string) =>
        request<Case>({
            method: 'POST',
            url: '/cases',
            data: { external_reference: externalReference },
        }),
};

// =============================================================================
// Scenarios API
// =============================================================================
export interface Scenario {
    id: string;
    program_name: string;
    program_id: string;
    status: 'eligible' | 'refer' | 'not_eligible';
    confidence_score: number;
    pricing?: {
        apr: number;
        monthly_payment: number;
        total_cost: number;
        term_months: number;
    };
    reason_codes?: string[];
    explanation?: {
        summary: { outcome: string; confidence: number; plain_english: string };
        factors: Array<{ name: string; impact: string; weight: number; value: string; description: string }>;
        rules: Array<{ rule_id: string; rule_name: string; passed: boolean; explanation: string }>;
        data: Array<{ field: string; value: string; source: string; confidence: number }>;
    };
}

export interface ScenarioRun {
    id: string;
    case_id: string;
    intake_snapshot_id: string;
    total_scenarios: number;
    eligible_count: number;
    refer_count: number;
    not_eligible_count: number;
    created_at: string;
}

export interface RankingMode {
    mode: 'best_fit' | 'lowest_payment' | 'fastest_close' | 'highest_approval';
}

export const scenarios = {
    runScenarios: (caseId: string, intakeSnapshotId: string) =>
        request<ScenarioRun>({
            method: 'POST',
            url: `/cases/${caseId}/scenarios/run`,
            data: { intake_snapshot_id: intakeSnapshotId },
        }),

    listRuns: (caseId: string, limit = 10) =>
        request<ScenarioRun[]>({
            method: 'GET',
            url: `/cases/${caseId}/scenarios/runs`,
            params: { limit },
        }),

    getRun: (caseId: string, runId: string) =>
        request<{
            scenario_run_id: string;
            total: number;
            eligible: Scenario[];
            refer: Scenario[];
            not_eligible: Scenario[];
        }>({
            method: 'GET',
            url: `/cases/${caseId}/scenarios/runs/${runId}`,
        }),

    getRankings: (caseId: string, runId: string, mode: RankingMode['mode']) =>
        request<{
            ranked_scenarios: Scenario[];
            gated_scenarios: Scenario[];
        }>({
            method: 'POST',
            url: `/cases/${caseId}/scenarios/runs/${runId}/rankings`,
            data: { mode },
        }),

    simulate: (caseId: string, hypotheticalChanges: Record<string, unknown>) =>
        request<{
            case_id: string;
            hypothetical_changes: Record<string, unknown>;
            status_changes: Array<{ scenario_id: string; old_status: string; new_status: string }>;
            changes_summary: string;
            confidence: number;
            confidence_reason: string;
            disclaimer: string;
        }>({
            method: 'POST',
            url: `/cases/${caseId}/scenarios/simulate`,
            data: { hypothetical_changes: hypotheticalChanges },
        }),
};

// =============================================================================
// Alternative Data (Plaid) API
// =============================================================================
export interface PlaidAccount {
    id: string;
    name: string;
    type: string;
    balance: number;
    currency: string;
    institution_name: string;
    connected_at: string;
}

export const alternativeData = {
    getLinkToken: (caseId: string) =>
        request<{ link_token: string; expiration: string }>({
            method: 'POST',
            url: `/cases/${caseId}/alt-data/link-token`,
        }),

    exchangeToken: (caseId: string, publicToken: string) =>
        request<{ success: boolean; accounts: PlaidAccount[] }>({
            method: 'POST',
            url: `/cases/${caseId}/alt-data/exchange`,
            data: { public_token: publicToken },
        }),

    listAccounts: (caseId: string) =>
        request<PlaidAccount[]>({
            method: 'GET',
            url: `/cases/${caseId}/alt-data/accounts`,
        }),

    disconnectAccount: (caseId: string, accountId: string) =>
        request<{ success: boolean }>({
            method: 'DELETE',
            url: `/cases/${caseId}/alt-data/accounts/${accountId}`,
        }),
};

// =============================================================================
// Pulse Alerts API
// =============================================================================
export interface PulseAlert {
    id: string;
    type: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    summary: string;
    impact_description: string;
    triggered_at: string;
    acknowledged_at?: string;
}

export interface PulseSubscription {
    id: string;
    case_id: string;
    enabled: boolean;
    frequency: 'realtime' | 'daily' | 'weekly';
    created_at: string;
}

export const pulse = {
    listAlerts: (caseId: string, limit = 20) =>
        request<PulseAlert[]>({
            method: 'GET',
            url: `/cases/${caseId}/pulse/alerts`,
            params: { limit },
        }),

    acknowledgeAlert: (caseId: string, alertId: string) =>
        request<{ success: boolean }>({
            method: 'POST',
            url: `/cases/${caseId}/pulse/alerts/${alertId}/acknowledge`,
        }),

    getSubscription: (caseId: string) =>
        request<PulseSubscription>({
            method: 'GET',
            url: `/cases/${caseId}/pulse/subscription`,
        }),

    updateSubscription: (caseId: string, enabled: boolean, frequency?: string) =>
        request<PulseSubscription>({
            method: 'PUT',
            url: `/cases/${caseId}/pulse/subscription`,
            data: { enabled, frequency },
        }),
};

// =============================================================================
// Consents API
// =============================================================================
export interface Consent {
    id: string;
    case_id: string;
    consent_type: string;
    purpose: string;
    granted: boolean;
    granted_at?: string;
    revoked_at?: string;
    expires_at?: string;
}

export const consents = {
    list: (caseId: string) =>
        request<Consent[]>({
            method: 'GET',
            url: `/cases/${caseId}/consents`,
        }),

    grant: (caseId: string, consentType: string, purpose: string) =>
        request<Consent>({
            method: 'POST',
            url: `/cases/${caseId}/consents`,
            data: { consent_type: consentType, purpose },
        }),

    revoke: (caseId: string, consentId: string) =>
        request<{ success: boolean; downstream_disabled: boolean }>({
            method: 'POST',
            url: `/cases/${caseId}/consents/${consentId}/revoke`,
        }),
};

// =============================================================================
// Retention API
// =============================================================================
export interface RetentionSetting {
    data_category: string;
    retention_days: number;
    can_modify: boolean;
    last_modified?: string;
}

export const retention = {
    getSettings: (caseId: string) =>
        request<RetentionSetting[]>({
            method: 'GET',
            url: `/cases/${caseId}/retention`,
        }),

    updateSetting: (caseId: string, dataCategory: string, retentionDays: number) =>
        request<RetentionSetting>({
            method: 'PUT',
            url: `/cases/${caseId}/retention/${dataCategory}`,
            data: { retention_days: retentionDays },
        }),

    requestDeletion: (caseId: string, dataCategories: string[]) =>
        request<{ deletion_id: string; scheduled_for: string }>({
            method: 'POST',
            url: `/cases/${caseId}/retention/delete`,
            data: { data_categories: dataCategories },
        }),
};

// =============================================================================
// Exports API
// =============================================================================
export const exports = {
    requestExport: (caseId: string, format: 'json' | 'csv' | 'pdf', type: 'consumer' | 'pro' | 'compliance') =>
        request<{ export_id: string; status: string }>({
            method: 'POST',
            url: `/cases/${caseId}/exports`,
            data: { format, export_type: type },
        }),

    getExportStatus: (caseId: string, exportId: string) =>
        request<{ status: string; download_url?: string; expires_at?: string }>({
            method: 'GET',
            url: `/cases/${caseId}/exports/${exportId}`,
        }),

    listExports: (caseId: string) =>
        request<Array<{ id: string; format: string; type: string; status: string; created_at: string }>>({
            method: 'GET',
            url: `/cases/${caseId}/exports`,
        }),
};

// =============================================================================
// Access Log API
// =============================================================================
export interface AccessLogEntry {
    id: string;
    resource_type: string;
    resource_id: string;
    action: string;
    accessor_id: string;
    accessor_role: string;
    accessed_at: string;
    ip_address?: string;
    purpose?: string;
}

export const accessLog = {
    list: (caseId: string, limit = 50, resourceType?: string) =>
        request<AccessLogEntry[]>({
            method: 'GET',
            url: `/cases/${caseId}/access-log`,
            params: { limit, resource_type: resourceType },
        }),

    export: (caseId: string, format: 'json' | 'csv' = 'csv') =>
        request<{ download_url: string }>({
            method: 'POST',
            url: `/cases/${caseId}/access-log/export`,
            data: { format },
        }),
};

// =============================================================================
// Agents API
// =============================================================================
export interface AgentMessage {
    id: string;
    role: 'user' | 'agent';
    agent_type?: string;
    content: string;
    created_at: string;
    actions?: Array<{ type: string; label: string; payload: unknown }>;
}

export const agents = {
    sendMessage: (caseId: string, message: string) =>
        request<AgentMessage>({
            method: 'POST',
            url: `/cases/${caseId}/chat`,
            data: { message },
        }),

    getChatHistory: (caseId: string, limit = 50) =>
        request<AgentMessage[]>({
            method: 'GET',
            url: `/cases/${caseId}/chat/history`,
            params: { limit },
        }),

    getCoachSuggestions: (caseId: string) =>
        request<Array<{ id: string; suggestion: string; impact: string; action_type: string }>>({
            method: 'GET',
            url: `/cases/${caseId}/coach/suggestions`,
        }),
};

// =============================================================================
// Admin APIs
// =============================================================================
export const admin = {
    // Programs
    getPrograms: () => request<Array<unknown>>({ method: 'GET', url: '/programs' }),
    getProgram: (id: string) => request<unknown>({ method: 'GET', url: `/programs/${id}` }),
    createProgram: (data: unknown) => request<unknown>({ method: 'POST', url: '/programs', data }),
    updateProgram: (id: string, data: unknown) => request<unknown>({ method: 'PUT', url: `/programs/${id}`, data }),
    deprecateProgram: (id: string) => request<unknown>({ method: 'POST', url: `/programs/${id}/deprecate` }),

    // Rulesets
    getRulesets: () => request<Array<unknown>>({ method: 'GET', url: '/rulesets' }),
    getRuleset: (id: string) => request<unknown>({ method: 'GET', url: `/rulesets/${id}` }),
    createRuleset: (data: unknown) => request<unknown>({ method: 'POST', url: '/rulesets', data }),
    updateRuleset: (id: string, data: unknown) => request<unknown>({ method: 'PUT', url: `/rulesets/${id}`, data }),

    // Reason Codes
    getReasonCodes: () => request<Array<unknown>>({ method: 'GET', url: '/reason-codes' }),

    // Review Queue
    getReviewQueue: () => request<Array<unknown>>({ method: 'GET', url: '/review/queue' }),
    assignReview: (id: string, reviewerId: string) =>
        request<unknown>({ method: 'POST', url: `/review/${id}/assign`, data: { reviewer_id: reviewerId } }),
    submitReview: (id: string, decision: string, notes: string) =>
        request<unknown>({ method: 'POST', url: `/review/${id}/submit`, data: { decision, notes } }),

    // Audit
    getAuditSnapshots: () => request<Array<unknown>>({ method: 'GET', url: '/audit/snapshots' }),
    getAuditSnapshot: (id: string) => request<unknown>({ method: 'GET', url: `/audit/snapshots/${id}` }),
};

// =============================================================================
// Fairness APIs
// =============================================================================
export const fairness = {
    getMetrics: () => request<unknown>({ method: 'GET', url: '/fairness/metrics' }),
    getProtectedAttributes: () => request<Array<unknown>>({ method: 'GET', url: '/fairness/protected-attributes' }),

    // Test History
    getTestHistory: (limit = 20) =>
        request<Array<unknown>>({ method: 'GET', url: '/fairness/tests', params: { limit } }),
    getTestDetails: (id: string) =>
        request<unknown>({ method: 'GET', url: `/fairness/tests/${id}` }),

    // LDA Search
    startLDASearch: (programId: string, attribute: string) =>
        request<unknown>({ method: 'POST', url: '/fairness/lda-search', data: { program_id: programId, protected_attribute: attribute } }),
    getLDASearchResults: (searchId: string) =>
        request<unknown>({ method: 'GET', url: `/fairness/lda-search/${searchId}` }),

    // CI/CD Artifacts
    getArtifacts: () => request<Array<unknown>>({ method: 'GET', url: '/fairness/artifacts' }),
    downloadArtifact: (id: string) => request<{ url: string }>({ method: 'GET', url: `/fairness/artifacts/${id}/download` }),

    // Monitoring
    getMonitoringMetrics: () => request<unknown>({ method: 'GET', url: '/fairness/monitoring' }),
    getAlerts: () => request<Array<unknown>>({ method: 'GET', url: '/fairness/alerts' }),
};

// =============================================================================
// Partners (LaaS) APIs
// =============================================================================
export const partners = {
    list: () => request<Array<unknown>>({ method: 'GET', url: '/partners' }),
    get: (id: string) => request<unknown>({ method: 'GET', url: `/partners/${id}` }),
    create: (data: unknown) => request<unknown>({ method: 'POST', url: '/partners', data }),
    update: (id: string, data: unknown) => request<unknown>({ method: 'PUT', url: `/partners/${id}`, data }),
    regenerateApiKey: (id: string) => request<{ api_key: string }>({ method: 'POST', url: `/partners/${id}/regenerate-key` }),

    // Audit Log
    getAuditLog: (partnerId?: string, limit = 50) =>
        request<Array<unknown>>({ method: 'GET', url: '/partners/audit-log', params: { partner_id: partnerId, limit } }),

    // Usage Stats
    getUsageStats: (partnerId: string) =>
        request<unknown>({ method: 'GET', url: `/partners/${partnerId}/usage` }),
};

// =============================================================================
// Feature Flags APIs
// =============================================================================
export const featureFlags = {
    list: () => request<Array<{
        key: string;
        name: string;
        description: string;
        current_value: boolean;
        category: string;
    }>>({ method: 'GET', url: '/feature-flags' }),

    get: (key: string) =>
        request<unknown>({ method: 'GET', url: `/feature-flags/${key}` }),

    update: (key: string, value: boolean) =>
        request<unknown>({ method: 'PATCH', url: `/feature-flags/${key}`, data: { value } }),
};

// =============================================================================
// Default export
// =============================================================================
export default {
    auth,
    cases,
    scenarios,
    alternativeData,
    pulse,
    consents,
    retention,
    exports,
    accessLog,
    agents,
    admin,
    fairness,
    partners,
    featureFlags,
    setAuthToken,
    getAuthToken,
};
