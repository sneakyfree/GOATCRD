import js from '@eslint/js';
import tsParser from '@typescript-eslint/parser';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from 'globals';

export default [
    {
        ignores: [
            'dist/**',
            'node_modules/**',
            'playwright-report/**',
            'test-results/**',
            'coverage/**',
        ],
    },
    js.configs.recommended,
    {
        files: ['**/*.{ts,tsx}'],
        languageOptions: {
            parser: tsParser,
            parserOptions: {
                ecmaVersion: 'latest',
                sourceType: 'module',
                ecmaFeatures: { jsx: true },
            },
            globals: {
                ...globals.browser,
                ...globals.es2021,
            },
        },
        plugins: {
            '@typescript-eslint': tsPlugin,
            'react-hooks': reactHooks,
            'react-refresh': reactRefresh,
        },
        rules: {
            ...tsPlugin.configs.recommended.rules,
            ...reactHooks.configs.recommended.rules,
            'react-refresh/only-export-components': [
                'warn',
                { allowConstantExport: true },
            ],
            // TypeScript resolves identifiers itself and understands lib/DOM
            // types, so the base rule only produces false positives here. It
            // flagged self, caches, fetch, Response, URL and React as
            // undefined. This is the documented typescript-eslint guidance.
            'no-undef': 'off',
            // tsc already reports unused symbols via noUnusedLocals /
            // noUnusedParameters, so the base rule would double-report and
            // misfires on type-only identifiers.
            'no-unused-vars': 'off',
            '@typescript-eslint/no-unused-vars': [
                'error',
                { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
            ],
            // Aspirational rather than a defect: the existing `any` uses are
            // deliberate escape hatches. Surfaced, but not a merge blocker.
            '@typescript-eslint/no-explicit-any': 'warn',
        },
    },
    {
        // The service worker is plain JS with its own global scope
        // (self, caches, clients), not the window scope.
        files: ['public/sw.js'],
        languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'script',
            globals: {
                ...globals.serviceworker,
                ...globals.browser,
            },
        },
    },
    {
        // Playwright specs run in Node, not the browser.
        files: ['e2e/**/*.{ts,tsx}'],
        languageOptions: {
            globals: { ...globals.node },
        },
    },
    {
        // Config files are Node-side ESM.
        files: ['*.config.{js,ts}', 'vite.config.ts', 'playwright.config.ts'],
        languageOptions: {
            globals: { ...globals.node },
        },
    },
];
