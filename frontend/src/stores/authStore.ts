import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from 'axios';

interface User {
    id: string;
    email: string;
    first_name: string | null;
    last_name: string | null;
    role: string;
}

interface AuthState {
    user: User | null;
    accessToken: string | null;
    refreshToken: string | null;
    isLoading: boolean;
    error: string | null;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string) => Promise<void>;
    logout: () => void;
    clearError: () => void;
}

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            user: null,
            accessToken: null,
            refreshToken: null,
            isLoading: false,
            error: null,

            login: async (email: string, password: string) => {
                set({ isLoading: true, error: null });
                try {
                    const response = await axios.post(`${API_URL}/auth/login`, {
                        email,
                        password,
                    });

                    const { access_token, refresh_token } = response.data;

                    // Get user info
                    const userResponse = await axios.get(`${API_URL}/auth/me`, {
                        headers: { Authorization: `Bearer ${access_token}` },
                    });

                    set({
                        user: userResponse.data,
                        accessToken: access_token,
                        refreshToken: refresh_token,
                        isLoading: false,
                    });
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Login failed',
                        isLoading: false,
                    });
                    throw error;
                }
            },

            register: async (email: string, password: string) => {
                set({ isLoading: true, error: null });
                try {
                    await axios.post(`${API_URL}/auth/register`, {
                        email,
                        password,
                    });

                    // Auto-login after registration
                    await get().login(email, password);
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Registration failed',
                        isLoading: false,
                    });
                    throw error;
                }
            },

            logout: () => {
                set({
                    user: null,
                    accessToken: null,
                    refreshToken: null,
                    error: null,
                });
            },

            clearError: () => {
                set({ error: null });
            },
        }),
        {
            name: 'goatcrd-auth',
            partialize: (state) => ({
                user: state.user,
                accessToken: state.accessToken,
                refreshToken: state.refreshToken,
            }),
        }
    )
);
