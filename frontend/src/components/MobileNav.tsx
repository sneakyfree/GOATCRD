import { NavLink, useLocation } from 'react-router-dom';

interface NavItem {
    path: string;
    label: string;
    icon: string;
}

const NAV_ITEMS: NavItem[] = [
    { path: '/', label: 'Home', icon: '🏠' },
    { path: '/scenarios', label: 'Scenarios', icon: '📊' },
    { path: '/what-if', label: 'What-If', icon: '🔮' },
    { path: '/my-data', label: 'My Data', icon: '📁' },
];

/**
 * MobileNav Component
 * 
 * Fixed bottom navigation for mobile devices.
 * - Shows 4 primary navigation items
 * - Respects safe area insets for notched devices
 * - Hidden on desktop (md breakpoint and up)
 */
export function MobileNav() {
    const location = useLocation();

    const isActive = (path: string) => {
        if (path === '/') return location.pathname === '/';
        return location.pathname.startsWith(path);
    };

    return (
        <nav className="mobile-nav safe-area-bottom md:hidden">
            <div className="flex justify-around items-center">
                {NAV_ITEMS.map(item => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={`mobile-nav-item ${isActive(item.path) ? 'active' : ''}`}
                    >
                        <span className="text-xl mb-1">{item.icon}</span>
                        <span className="text-xs">{item.label}</span>
                    </NavLink>
                ))}
            </div>
        </nav>
    );
}

/**
 * MobileHeader Component
 * 
 * Sticky header for mobile with page title and actions.
 */
interface MobileHeaderProps {
    title: string;
    subtitle?: string;
    showBack?: boolean;
    onBack?: () => void;
    actions?: React.ReactNode;
}

export function MobileHeader({
    title,
    subtitle,
    showBack = false,
    onBack,
    actions
}: MobileHeaderProps) {
    return (
        <header className="sticky top-0 z-40 bg-gray-900/95 backdrop-blur-lg border-b border-white/10 safe-area-top">
            <div className="flex items-center h-14 px-4">
                {showBack && (
                    <button
                        onClick={onBack}
                        className="mr-3 w-10 h-10 flex items-center justify-center rounded-full hover:bg-white/10 touch-target"
                        aria-label="Go back"
                    >
                        ←
                    </button>
                )}
                <div className="flex-1 min-w-0">
                    <h1 className="text-lg font-semibold truncate">{title}</h1>
                    {subtitle && (
                        <p className="text-xs text-white/50 truncate">{subtitle}</p>
                    )}
                </div>
                {actions && (
                    <div className="flex items-center gap-2 ml-3">
                        {actions}
                    </div>
                )}
            </div>
        </header>
    );
}

/**
 * BottomSheet Component
 * 
 * Mobile-friendly bottom sheet for modals and action panels.
 */
interface BottomSheetProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    children: React.ReactNode;
}

export function BottomSheet({ isOpen, onClose, title, children }: BottomSheetProps) {
    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/50 z-40 transition-opacity"
                onClick={onClose}
            />

            {/* Sheet */}
            <div className={`bottom-sheet ${isOpen ? 'open' : ''}`}>
                <div className="bottom-sheet-handle" onClick={onClose} />

                {title && (
                    <div className="px-4 pb-3 border-b border-white/10">
                        <h2 className="text-lg font-semibold">{title}</h2>
                    </div>
                )}

                <div className="overflow-y-auto max-h-[80vh] p-4">
                    {children}
                </div>
            </div>
        </>
    );
}

/**
 * FloatingActionButton Component
 * 
 * Primary action button for mobile, positioned bottom-right.
 */
interface FABProps {
    icon: string;
    label?: string;
    onClick: () => void;
    variant?: 'primary' | 'secondary';
}

export function FloatingActionButton({
    icon,
    label,
    onClick,
    variant = 'primary'
}: FABProps) {
    return (
        <button
            onClick={onClick}
            className={`fab ${variant === 'secondary' ? 'bg-white/10' : ''}`}
            aria-label={label || icon}
        >
            <span className="text-2xl">{icon}</span>
        </button>
    );
}

/**
 * PullToRefresh Component
 * 
 * Pull-to-refresh wrapper for mobile content areas.
 */
interface PullToRefreshProps {
    onRefresh: () => Promise<void>;
    children: React.ReactNode;
}

export function PullToRefresh({ onRefresh: _onRefresh, children }: PullToRefreshProps) {
    // Note: Full implementation would require touch event handling
    // This is a placeholder structure for the pattern
    return (
        <div className="pull-to-refresh-area">
            {children}
        </div>
    );
}

/**
 * SwipeableCard Component
 * 
 * Card that supports swipe gestures for actions.
 */
interface SwipeableCardProps {
    children: React.ReactNode;
    onSwipeLeft?: () => void;
    onSwipeRight?: () => void;
    leftAction?: { label: string; color: string };
    rightAction?: { label: string; color: string };
}

export function SwipeableCard({
    children,
    leftAction,
    rightAction
}: SwipeableCardProps) {
    // Note: Full implementation would require touch event handling
    return (
        <div className="relative overflow-hidden rounded-xl">
            {/* Action areas */}
            {leftAction && (
                <div className={`absolute left-0 inset-y-0 w-20 flex items-center justify-center ${leftAction.color}`}>
                    {leftAction.label}
                </div>
            )}
            {rightAction && (
                <div className={`absolute right-0 inset-y-0 w-20 flex items-center justify-center ${rightAction.color}`}>
                    {rightAction.label}
                </div>
            )}

            {/* Content */}
            <div className="relative bg-gray-800 z-10">
                {children}
            </div>
        </div>
    );
}

/**
 * EmptyState Component
 * 
 * Mobile-friendly empty state with illustration and action.
 */
interface EmptyStateProps {
    icon: string;
    title: string;
    description: string;
    actionLabel?: string;
    onAction?: () => void;
}

export function EmptyState({
    icon,
    title,
    description,
    actionLabel,
    onAction
}: EmptyStateProps) {
    return (
        <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
            <span className="text-6xl mb-4">{icon}</span>
            <h3 className="text-lg font-semibold mb-2">{title}</h3>
            <p className="text-white/60 text-sm mb-6 max-w-xs">{description}</p>
            {actionLabel && onAction && (
                <button
                    onClick={onAction}
                    className="btn-primary touch-target"
                >
                    {actionLabel}
                </button>
            )}
        </div>
    );
}

/**
 * LoadingSkeleton Component
 * 
 * Skeleton loading state for mobile.
 */
interface LoadingSkeletonProps {
    type: 'card' | 'list' | 'text';
    count?: number;
}

export function LoadingSkeleton({ type, count = 3 }: LoadingSkeletonProps) {
    const items = Array.from({ length: count }, (_, i) => i);

    if (type === 'card') {
        return (
            <div className="grid-mobile-stack">
                {items.map(i => (
                    <div key={i} className="glass-card">
                        <div className="skeleton h-32 rounded-lg mb-4" />
                        <div className="skeleton-text w-3/4 mb-2" />
                        <div className="skeleton-text w-1/2" />
                    </div>
                ))}
            </div>
        );
    }

    if (type === 'list') {
        return (
            <div className="space-y-3">
                {items.map(i => (
                    <div key={i} className="flex items-center gap-4 p-4 bg-white/5 rounded-lg">
                        <div className="skeleton-circle w-12 h-12" />
                        <div className="flex-1">
                            <div className="skeleton-text w-2/3 mb-2" />
                            <div className="skeleton-text w-1/3" />
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    return (
        <div className="space-y-2">
            {items.map(i => (
                <div key={i} className="skeleton-text" style={{ width: `${70 + Math.random() * 30}%` }} />
            ))}
        </div>
    );
}

export default MobileNav;
