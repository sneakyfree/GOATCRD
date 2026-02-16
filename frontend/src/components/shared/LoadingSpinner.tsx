import React from 'react';
import './LoadingSpinner.css';

interface LoadingSpinnerProps {
    /** Size variant */
    size?: 'sm' | 'md' | 'lg';
    /** Optional text to display below spinner */
    label?: string;
    /** Whether to display inline or as full container */
    inline?: boolean;
}

/**
 * Branded loading spinner with smooth animation.
 * Used across pages during data fetching.
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
    size = 'md',
    label,
    inline = false,
}) => {
    const sizeMap = { sm: 20, md: 36, lg: 56 };
    const px = sizeMap[size];

    return (
        <div className={`loading-spinner-container ${inline ? 'inline' : 'full'}`}>
            <div
                className="loading-spinner"
                style={{ width: px, height: px }}
                role="status"
                aria-label={label || 'Loading'}
            />
            {label && <span className="loading-spinner-label">{label}</span>}
        </div>
    );
};

interface SkeletonCardProps {
    /** Number of skeleton lines */
    lines?: number;
    /** Whether to show a header block */
    withHeader?: boolean;
}

/**
 * Skeleton loading card for content placeholders.
 * Provides shimmer animation while real data loads.
 */
export const SkeletonCard: React.FC<SkeletonCardProps> = ({
    lines = 3,
    withHeader = true,
}) => {
    return (
        <div className="skeleton-card" role="status" aria-label="Loading content">
            {withHeader && <div className="skeleton-line skeleton-header" />}
            {Array.from({ length: lines }).map((_, i) => (
                <div
                    key={i}
                    className="skeleton-line"
                    style={{ width: `${85 - i * 10}%` }}
                />
            ))}
        </div>
    );
};

/**
 * Data source badge indicating live vs mock data.
 */
export const DataSourceBadge: React.FC<{ source: 'live' | 'mock' }> = ({ source }) => {
    return (
        <span className={`data-source-badge ${source}`}>
            <span className="data-source-dot" />
            {source === 'live' ? 'Live Data' : 'Demo Data'}
        </span>
    );
};

export default LoadingSpinner;
