/**
 * GOATCRD Feature Flags
 * Runtime feature flag system reading from environment variables.
 * All flags default to false/disabled for safety.
 */

type FeatureFlagKey =
    | 'plaid_live'
    | 'rich_editor'
    | 'email_delivery'
    | 'sms_delivery'
    | 'stripe_live'
    | 'ab_testing'
    | 'pulse_realtime';

// Map feature flags to Vite env vars
const FLAG_ENV_MAP: Record<FeatureFlagKey, string> = {
    plaid_live: 'VITE_PLAID_ENABLED',
    rich_editor: 'VITE_RICH_EDITOR',
    email_delivery: 'VITE_EMAIL_DELIVERY',
    sms_delivery: 'VITE_SMS_DELIVERY',
    stripe_live: 'VITE_STRIPE_LIVE',
    ab_testing: 'VITE_AB_TESTING',
    pulse_realtime: 'VITE_PULSE_REALTIME',
};

/**
 * Check if a feature flag is enabled.
 * Reads from import.meta.env (Vite environment variables).
 */
export function isFeatureEnabled(flag: FeatureFlagKey): boolean {
    const envVar = FLAG_ENV_MAP[flag];
    if (!envVar) return false;

    const value = (import.meta as any).env?.[envVar];
    return value === 'true' || value === '1';
}

/**
 * Get all feature flag statuses (useful for debugging/admin views).
 */
export function getAllFeatureFlags(): Record<FeatureFlagKey, boolean> {
    const flags: Partial<Record<FeatureFlagKey, boolean>> = {};
    for (const key of Object.keys(FLAG_ENV_MAP) as FeatureFlagKey[]) {
        flags[key] = isFeatureEnabled(key);
    }
    return flags as Record<FeatureFlagKey, boolean>;
}

/**
 * Data source indicator — is this feature using live or mock data?
 */
export function getDataSourceLabel(flag: FeatureFlagKey): 'live' | 'mock' {
    return isFeatureEnabled(flag) ? 'live' : 'mock';
}
