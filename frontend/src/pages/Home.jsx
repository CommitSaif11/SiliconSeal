import { Link } from 'react-router-dom';
import { Shield, Cpu, Eye, Brain, Layers, ScanLine, Upload, Camera, Lock, Zap, Database, Bot } from 'lucide-react';
import { useBackendStatus } from '../hooks/useBackendStatus';

const FEATURES = [
  { icon: Eye, title: 'YOLO Detection', desc: 'YOLOv8 deep learning model detects and crops IC chips from images automatically.' },
  { icon: ScanLine, title: 'PaddleOCR Engine', desc: 'Multi-pass OCR with confidence filtering reads part codes, date codes, and lot codes.' },
  { icon: Cpu, title: 'Dual Verification', desc: 'Regex (known IC) and Aho-Corasick (auto-detect) algorithms for flexible verification.' },
  { icon: Brain, title: 'AI Agent Layer', desc: 'Groq-powered Llama 3.3 70B analyzes results and provides risk assessment in natural language.' },
  { icon: Lock, title: 'JWT Authentication', desc: 'Secure admin endpoints with bcrypt password hashing and Bearer token auth.' },
  { icon: Database, title: 'Knowledge Base', desc: '27+ IC entries with OCR-tolerant regex patterns for STM32, ATmega, INA, and more.' },
];

const PIPELINE_STEPS = [
  { num: '01', title: 'Image Input', desc: 'Upload, camera capture, or batch of IC images', icon: Upload },
  { num: '02', title: 'YOLO Detection', desc: 'Detect and crop IC region from image', icon: Eye },
  { num: '03', title: 'PaddleOCR', desc: 'Multi-pass text extraction with confidence scoring', icon: ScanLine },
  { num: '04', title: 'Pattern Matching', desc: 'Regex or Aho-Corasick verification against KB', icon: Cpu },
  { num: '05', title: 'Scoring Engine', desc: 'Weighted scoring: 60% part, 25% date, 15% lot', icon: Zap },
  { num: '06', title: 'AI Analysis', desc: 'LLM-powered verdict explanation and risk assessment', icon: Bot },
];

const TECH_STACK = [
  { category: 'Backend', items: ['FastAPI', 'Python 3.10+', 'Uvicorn', 'Pydantic'] },
  { category: 'ML / CV', items: ['YOLOv8 (Ultralytics)', 'PaddleOCR', 'OpenCV', 'NumPy'] },
  { category: 'Algorithms', items: ['Aho-Corasick Trie', 'Regex Engine', 'Weighted Scoring', 'YYWW Date Validation'] },
  { category: 'AI Agent', items: ['Groq API', 'Llama 3.3 70B', 'Structured JSON Output', 'Risk Analysis'] },
  { category: 'Frontend', items: ['React 19', 'Vite', 'Tailwind CSS', 'Framer Motion'] },
  { category: 'Security', items: ['JWT (python-jose)', 'bcrypt', 'CORS Whitelist', 'Input Validation'] },
];

export default function Home() {
  const { status } = useBackendStatus();

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative overflow-hidden px-4 pt-20 pb-28">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-accent-50 dark:from-gray-900 dark:via-gray-900 dark:to-primary-900/20" />
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-400/20 rounded-full blur-3xl" />
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-accent-400/10 rounded-full blur-3xl" />

        <div className="relative max-w-5xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-500/10 text-primary-600 dark:text-primary-400 text-sm font-medium border border-primary-500/20">
            <Shield className="w-4 h-4" />
            SIH 2025 Finalist — Problem Statement ID: 25162
          </div>

          <h1 className="text-5xl sm:text-7xl font-black tracking-tight">
            <span className="gradient-text">SiliconSeal</span>
          </h1>

          <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Automated Optical Inspection system for <strong>IC marking verification</strong> and{' '}
            <strong>counterfeit detection</strong>, built for{' '}
            <span className="text-primary-600 dark:text-primary-400 font-semibold">Bharat Electronics Limited (BEL)</span>
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              to="/scan"
              className="inline-flex items-center gap-2 px-8 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-xl font-semibold transition-all shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40"
            >
              <ScanLine className="w-5 h-5" />
              Start Scanning
            </Link>
            <Link
              to="/architecture"
              className="inline-flex items-center gap-2 px-8 py-3 border border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500 rounded-xl font-semibold text-gray-700 dark:text-gray-300 transition-all"
            >
              <Layers className="w-5 h-5" />
              View Architecture
            </Link>
          </div>

          <div className="flex items-center justify-center gap-2 pt-2">
            <div className={`w-2 h-2 rounded-full ${
              status === 'online' ? 'bg-green-500 animate-pulse' : status === 'offline' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'
            }`} />
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Backend: {status === 'online' ? 'Connected' : status === 'offline' ? 'Offline' : 'Checking...'}
            </span>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="px-4 py-20 bg-gray-50/50 dark:bg-gray-800/30">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-4">Core Capabilities</h2>
          <p className="text-center text-gray-500 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
            A multi-layered system combining computer vision, NLP, and AI agents for comprehensive IC verification
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="p-6 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700/50 hover:border-primary-300 dark:hover:border-primary-500/30 transition-all hover:shadow-lg group">
                <Icon className="w-10 h-10 text-primary-500 mb-4 group-hover:text-accent-500 transition-colors" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{title}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline */}
      <section className="px-4 py-20">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-4">Verification Pipeline</h2>
          <p className="text-center text-gray-500 dark:text-gray-400 mb-12">
            End-to-end flow from image input to AI-powered verdict
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {PIPELINE_STEPS.map(({ num, title, desc, icon: Icon }) => (
              <div key={num} className="relative p-6 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700/50">
                <div className="absolute -top-3 -left-3 w-10 h-10 rounded-lg bg-primary-500 text-white flex items-center justify-center text-sm font-bold shadow-lg shadow-primary-500/30">
                  {num}
                </div>
                <div className="pt-2">
                  <Icon className="w-6 h-6 text-accent-500 mb-2" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">{title}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="px-4 py-20 bg-gray-50/50 dark:bg-gray-800/30">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">Technology Stack</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {TECH_STACK.map(({ category, items }) => (
              <div key={category} className="p-5 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700/50">
                <h3 className="text-sm font-bold text-primary-600 dark:text-primary-400 uppercase tracking-wider mb-3">{category}</h3>
                <div className="flex flex-wrap gap-2">
                  {items.map((item) => (
                    <span key={item} className="px-3 py-1 rounded-lg bg-gray-100 dark:bg-white/5 text-sm text-gray-700 dark:text-gray-300 font-medium">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* BEL Banner */}
      <section className="px-4 py-16">
        <div className="max-w-4xl mx-auto text-center p-8 rounded-2xl bg-gradient-to-r from-primary-500/10 via-accent-500/10 to-primary-500/10 border border-primary-500/20">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">Built for BEL India</h2>
          <p className="text-gray-600 dark:text-gray-300 mb-4 max-w-2xl mx-auto">
            Developed as part of Smart India Hackathon 2025 (Final Round) for Bharat Electronics Limited.
            Problem Statement ID: <strong>25162</strong> — Automated counterfeit IC detection using AOI.
          </p>
          <div className="flex justify-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1"><Camera className="w-4 h-4" /> Computer Vision</span>
            <span className="flex items-center gap-1"><Brain className="w-4 h-4" /> AI Agents</span>
            <span className="flex items-center gap-1"><Shield className="w-4 h-4" /> Defense Grade</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-4 py-8 border-t border-gray-200 dark:border-gray-800">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-500 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-primary-500" />
            <span className="font-semibold gradient-text">SiliconSeal</span>
            <span>— SIH 2025 | BEL India</span>
          </div>
          <div>Built by Saif</div>
        </div>
      </footer>
    </div>
  );
}
