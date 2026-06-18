import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import { Sun, Moon, Menu, X, Shield, LogOut, User, Award } from 'lucide-react';

const NAV_LINKS = [
  { to: '/', label: 'Home' },
  { to: '/scan', label: 'Scan' },
  { to: '/batch', label: 'Batch' },
  { to: '/live', label: 'Live Scan' },
  { to: '/architecture', label: 'Architecture' },
];

export default function Navbar() {
  const { dark, toggle } = useTheme();
  const { user, isAdmin, logout } = useAuth();
  const location = useLocation();
  const [open, setOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 glass">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-2 group">
              <motion.div
                whileHover={{ rotate: [0, -15, 15, 0] }}
                transition={{ duration: 0.5 }}
              >
                <Shield className="w-7 h-7 text-primary-500 group-hover:text-accent-500 transition-colors" />
              </motion.div>
              <span className="text-xl font-bold gradient-text">SiliconSeal</span>
            </Link>
            <div className="hidden lg:flex items-center gap-1.5">
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-500/20 flex items-center gap-1">
                <Award className="w-3 h-3" />
                SIH 2025
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20">
                BEL INDIA
              </span>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  location.pathname === to
                    ? 'bg-primary-500/10 text-primary-600 dark:text-primary-400'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/5'
                }`}
              >
                {label}
              </Link>
            ))}
            {isAdmin && (
              <Link
                to="/admin"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  location.pathname === '/admin'
                    ? 'bg-accent-500/10 text-accent-600 dark:text-accent-400'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/5'
                }`}
              >
                Admin
              </Link>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={toggle}
              className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-white/5 transition-colors"
              aria-label="Toggle theme"
            >
              {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>

            {user ? (
              <div className="hidden md:flex items-center gap-2">
                <span className="text-xs font-medium px-2 py-1 rounded-full bg-primary-500/10 text-primary-600 dark:text-primary-400">
                  <User className="w-3 h-3 inline mr-1" />
                  {user.username}
                </span>
                <button
                  onClick={logout}
                  className="p-2 rounded-lg text-gray-500 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-500/10 transition-colors"
                  aria-label="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="hidden md:inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg bg-primary-500 text-white hover:bg-primary-600 transition-colors"
              >
                Admin Login
              </Link>
            )}

            <button
              onClick={() => setOpen(!open)}
              className="md:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-white/5"
            >
              {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {open && (
          <div className="md:hidden pb-4 space-y-1">
            {NAV_LINKS.map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setOpen(false)}
                className={`block px-3 py-2 rounded-lg text-sm font-medium ${
                  location.pathname === to
                    ? 'bg-primary-500/10 text-primary-600 dark:text-primary-400'
                    : 'text-gray-600 dark:text-gray-300'
                }`}
              >
                {label}
              </Link>
            ))}
            {user ? (
              <button onClick={() => { logout(); setOpen(false); }} className="block w-full text-left px-3 py-2 rounded-lg text-sm text-red-500">
                Logout ({user.username})
              </button>
            ) : (
              <Link to="/login" onClick={() => setOpen(false)} className="block px-3 py-2 rounded-lg text-sm font-medium text-primary-500">
                Admin Login
              </Link>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
