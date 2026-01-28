import { useState } from 'react';

type RankingMode = 'best_fit' | 'lowest_payment' | 'fastest_close' | 'highest_approval';

interface RankingModeOption {
    id: RankingMode;
    label: string;
    description: string;
    icon: string;
}

interface RankingModeSelectorProps {
    currentMode: RankingMode;
    onModeChange: (mode: RankingMode) => void;
    disabled?: boolean;
}

const RANKING_MODES: RankingModeOption[] = [
    {
        id: 'best_fit',
        label: 'Best Fit',
        description: 'Overall best match for your profile',
        icon: '🎯'
    },
    {
        id: 'lowest_payment',
        label: 'Lowest Payment',
        description: 'Minimize monthly payment',
        icon: '💵'
    },
    {
        id: 'fastest_close',
        label: 'Fastest Close',
        description: 'Quickest time to funding',
        icon: '⚡'
    },
    {
        id: 'highest_approval',
        label: 'Highest Approval',
        description: 'Best chance of approval',
        icon: '✅'
    }
];

/**
 * RankingModeSelector Component
 * 
 * Allows users to select how scenarios are ranked/sorted.
 * Supports multiple ranking strategies with visual indicators.
 */
export function RankingModeSelector({
    currentMode,
    onModeChange,
    disabled = false
}: RankingModeSelectorProps) {
    const [isOpen, setIsOpen] = useState(false);

    const currentModeOption = RANKING_MODES.find(m => m.id === currentMode) || RANKING_MODES[0];

    return (
        <div className="relative">
            {/* Selected Mode Button */}
            <button
                onClick={() => !disabled && setIsOpen(!isOpen)}
                disabled={disabled}
                className={`flex items-center gap-3 bg-white/10 border border-white/20 rounded-lg px-4 py-3 w-full text-left transition-colors ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-white/15 hover:border-white/30'
                    }`}
            >
                <span className="text-xl">{currentModeOption.icon}</span>
                <div className="flex-1">
                    <p className="text-white font-medium">{currentModeOption.label}</p>
                    <p className="text-white/50 text-sm">{currentModeOption.description}</p>
                </div>
                <span className={`text-white/50 transition-transform ${isOpen ? 'rotate-180' : ''}`}>
                    ▼
                </span>
            </button>

            {/* Dropdown */}
            {isOpen && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-gray-900 border border-white/20 rounded-lg shadow-xl overflow-hidden z-50">
                    {RANKING_MODES.map(mode => (
                        <button
                            key={mode.id}
                            onClick={() => {
                                onModeChange(mode.id);
                                setIsOpen(false);
                            }}
                            className={`flex items-center gap-3 w-full px-4 py-3 text-left transition-colors ${mode.id === currentMode
                                    ? 'bg-purple-500/20 border-l-2 border-purple-500'
                                    : 'hover:bg-white/10'
                                }`}
                        >
                            <span className="text-xl">{mode.icon}</span>
                            <div className="flex-1">
                                <p className={`font-medium ${mode.id === currentMode ? 'text-purple-300' : 'text-white'
                                    }`}>
                                    {mode.label}
                                </p>
                                <p className="text-white/50 text-sm">{mode.description}</p>
                            </div>
                            {mode.id === currentMode && (
                                <span className="text-purple-400">✓</span>
                            )}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}

/**
 * RankingModeTabs Component
 * 
 * Horizontal tab-style selector for ranking modes.
 * More compact than dropdown version.
 */
export function RankingModeTabs({
    currentMode,
    onModeChange,
    disabled = false
}: RankingModeSelectorProps) {
    return (
        <div className="flex gap-2 bg-white/5 rounded-lg p-1">
            {RANKING_MODES.map(mode => (
                <button
                    key={mode.id}
                    onClick={() => !disabled && onModeChange(mode.id)}
                    disabled={disabled}
                    className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all ${mode.id === currentMode
                            ? 'bg-purple-500/30 text-purple-200'
                            : disabled
                                ? 'opacity-50 cursor-not-allowed text-white/40'
                                : 'text-white/60 hover:bg-white/10 hover:text-white'
                        }`}
                    title={mode.description}
                >
                    <span>{mode.icon}</span>
                    <span className="text-sm font-medium">{mode.label}</span>
                </button>
            ))}
        </div>
    );
}

export default RankingModeSelector;
