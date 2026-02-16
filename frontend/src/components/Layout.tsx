import { Outlet, Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { MobileNav } from './MobileNav';
import NotificationBell from './NotificationBell';

export function Layout() {
    const { user, logout } = useAuthStore();

    return (
        <div className="min-h-screen flex flex-col">
            {/* Desktop Navigation - hidden on mobile */}
            <nav className="glass border-b border-white/10 hidden md:block">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center">
                            <Link to="/" className="flex items-center">
                                <span className="text-2xl font-bold gradient-text">GOATCRD</span>
                            </Link>
                            <div className="ml-10">
                                <div className="flex items-center space-x-4">
                                    <Link to="/" className="text-white/70 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                                        Home
                                    </Link>
                                    <Link to="/scenarios" className="text-white/70 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                                        Scenarios
                                    </Link>
                                    <Link to="/what-if" className="text-white/70 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                                        What-If
                                    </Link>
                                    <Link to="/my-data" className="text-white/70 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                                        My Data
                                    </Link>
                                    <Link to="/faq" className="text-white/70 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                                        FAQ
                                    </Link>
                                    <Link to="/pricing" className="text-white/70 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                                        Pricing
                                    </Link>
                                    {user && (
                                        <Link to="/dashboard" className="text-white/70 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                                            Dashboard
                                        </Link>
                                    )}
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center space-x-4">
                            {user ? (
                                <>
                                    <NotificationBell />
                                    <span className="text-white/70 text-sm">{user.email}</span>
                                    <button
                                        onClick={logout}
                                        className="btn-secondary text-sm"
                                    >
                                        Logout
                                    </button>
                                </>
                            ) : (
                                <>
                                    <Link to="/login" className="btn-secondary text-sm">
                                        Login
                                    </Link>
                                    <Link to="/login" className="btn-primary text-sm">
                                        Get Started
                                    </Link>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </nav>

            {/* Mobile Header - visible on mobile only */}
            <header className="glass border-b border-white/10 md:hidden safe-area-top">
                <div className="flex items-center justify-between h-14 px-4">
                    <Link to="/" className="flex items-center">
                        <span className="text-xl font-bold gradient-text">GOATCRD</span>
                    </Link>
                    <div className="flex items-center gap-3">
                        {user ? (
                            <button
                                onClick={logout}
                                className="text-white/70 text-sm hover:text-white"
                            >
                                Logout
                            </button>
                        ) : (
                            <Link to="/login" className="btn-primary text-sm px-3 py-1.5">
                                Login
                            </Link>
                        )}
                    </div>
                </div>
            </header>

            {/* Main content - add bottom padding for mobile nav */}
            <main className="flex-1 container-responsive py-4 md:py-8 pb-20 md:pb-8">
                <Outlet />
            </main>

            {/* Footer - hidden on mobile */}
            <footer className="glass border-t border-white/10 mt-auto hidden md:block">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex items-center justify-between">
                        <p className="text-white/50 text-sm">
                            © 2026 GOATCRD. Compliance-first credit intelligence.
                        </p>
                        <div className="flex items-center space-x-6">
                            <a href="#" className="text-white/50 hover:text-white text-sm">Privacy</a>
                            <a href="#" className="text-white/50 hover:text-white text-sm">Terms</a>
                            <a href="#" className="text-white/50 hover:text-white text-sm">Contact</a>
                        </div>
                    </div>
                </div>
            </footer>

            {/* Mobile Bottom Navigation */}
            <MobileNav />
        </div>
    );
}

