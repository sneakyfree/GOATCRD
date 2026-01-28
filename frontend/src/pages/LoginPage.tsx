import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

export function LoginPage() {
    const navigate = useNavigate();
    const { login, register, isLoading, error, clearError } = useAuthStore();

    const [isRegister, setIsRegister] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        clearError();

        try {
            if (isRegister) {
                await register(email, password);
            } else {
                await login(email, password);
            }
            navigate('/dashboard');
        } catch {
            // Error is handled by the store
        }
    };

    return (
        <div className="max-w-md mx-auto py-12">
            <div className="glass-card">
                <h1 className="text-2xl font-bold text-center mb-6">
                    {isRegister ? 'Create Account' : 'Welcome Back'}
                </h1>

                {error && (
                    <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 mb-6">
                        <p className="text-red-400 text-sm">{error}</p>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-white/70 mb-1">
                            Email
                        </label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="input"
                            placeholder="you@example.com"
                            required
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-white/70 mb-1">
                            Password
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="input"
                            placeholder="••••••••"
                            required
                            minLength={8}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="btn-primary w-full py-3"
                    >
                        {isLoading ? 'Loading...' : isRegister ? 'Create Account' : 'Sign In'}
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <button
                        onClick={() => {
                            setIsRegister(!isRegister);
                            clearError();
                        }}
                        className="text-primary-400 hover:text-primary-300 text-sm"
                    >
                        {isRegister
                            ? 'Already have an account? Sign in'
                            : "Don't have an account? Create one"}
                    </button>
                </div>
            </div>
        </div>
    );
}
