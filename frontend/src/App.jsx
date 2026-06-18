import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import BackendBanner from './components/BackendBanner';
import PageTransition from './components/PageTransition';
import Home from './pages/Home';
import Scan from './pages/Scan';
import BatchScan from './pages/BatchScan';
import LiveScan from './pages/LiveScan';
import Login from './pages/Login';
import Admin from './pages/Admin';
import Architecture from './pages/Architecture';
import NotFound from './pages/NotFound';

function P({ children }) {
  return <PageTransition>{children}</PageTransition>;
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
        <Navbar />
        <BackendBanner />
        <Routes>
          <Route path="/" element={<P><Home /></P>} />
          <Route path="/scan" element={<P><Scan /></P>} />
          <Route path="/batch" element={<P><BatchScan /></P>} />
          <Route path="/live" element={<P><LiveScan /></P>} />
          <Route path="/login" element={<P><Login /></P>} />
          <Route path="/admin" element={<P><Admin /></P>} />
          <Route path="/architecture" element={<P><Architecture /></P>} />
          <Route path="*" element={<P><NotFound /></P>} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
