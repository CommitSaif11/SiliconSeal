import { Link } from 'react-router-dom';
import { Home, AlertTriangle } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4">
      <div className="text-center space-y-4">
        <AlertTriangle className="w-16 h-16 text-yellow-500 mx-auto" />
        <h1 className="text-6xl font-black gradient-text">404</h1>
        <p className="text-lg text-gray-500 dark:text-gray-400">Page not found</p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-6 py-2.5 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors"
        >
          <Home className="w-4 h-4" /> Back to Home
        </Link>
      </div>
    </div>
  );
}
