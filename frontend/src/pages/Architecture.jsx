import { Shield, Layers, Eye, ScanLine, Cpu, Brain, Lock, Database, Zap, Upload, Camera, Bot, Server, Globe, Code } from 'lucide-react';

const LAYERS = [
  {
    name: 'Presentation Layer',
    color: 'from-blue-500 to-blue-600',
    icon: Globe,
    desc: 'React + Vite frontend with Tailwind CSS, responsive design, dark/light mode',
    items: [
      'React 19 with React Router for SPA navigation',
      'Tailwind CSS v4 for utility-first styling',
      'Framer Motion for smooth UI transitions',
      'React Dropzone for drag-and-drop file upload',
      'Lucide React for consistent iconography',
      'Dark/Light theme with system preference detection',
      'Backend health monitoring with auto-retry',
      'Mobile-responsive design for field inspections',
    ],
  },
  {
    name: 'API Layer',
    color: 'from-green-500 to-green-600',
    icon: Server,
    desc: 'FastAPI REST endpoints with JWT auth, input validation, CORS protection',
    items: [
      'FastAPI 0.121+ with async/await throughout',
      'JWT authentication (python-jose + bcrypt)',
      'Upload size limits (10MB/file, 20 files/batch)',
      'Base64 input validation for live camera mode',
      'Configurable CORS whitelist (not wildcard)',
      'Pydantic schemas for request/response validation',
      'Auto-generated OpenAPI/Swagger documentation',
      'Health check endpoint for frontend status monitoring',
    ],
  },
  {
    name: 'Detection Layer (YOLO)',
    color: 'from-yellow-500 to-orange-500',
    icon: Eye,
    desc: 'YOLOv8 deep learning model for IC chip localization and cropping',
    items: [
      'YOLOv8n via Ultralytics for object detection',
      'Automatic IC region detection and cropping',
      'Configurable confidence & IOU thresholds',
      'CPU/CUDA/MPS device selection',
      'Graceful fallback to full image if detector unavailable',
      'Custom model path via environment variable',
      'Bounding box visualization support',
      'Padding-aware cropping for better OCR',
    ],
  },
  {
    name: 'OCR Layer (PaddleOCR)',
    color: 'from-cyan-500 to-teal-500',
    icon: ScanLine,
    desc: 'Multi-pass text extraction with confidence filtering and line grouping',
    items: [
      'PaddleOCR engine (English, textline orientation)',
      'Singleton pattern for efficient model reuse',
      'Confidence-based filtering (threshold: 0.80)',
      'Y-coordinate line grouping for multi-line IC markings',
      'Separate alphanumeric, numeric-only, alpha-only outputs',
      'OCR confusion correction (O↔0, I↔1, S↔5, B↔8)',
      'ThreadPoolExecutor for non-blocking async integration',
      'Average confidence scoring across all detected text',
    ],
  },
  {
    name: 'Verification Layer',
    color: 'from-purple-500 to-violet-500',
    icon: Cpu,
    desc: 'Dual algorithm engine: Regex (known IC) + Aho-Corasick (auto-detection)',
    items: [
      'Regex mode: Direct pattern matching against known part_id',
      'Aho-Corasick mode: Trie-based multi-pattern auto-detection',
      'Token extraction from part numbers, logos, alternatives',
      'Aggressive text normalization (case, spaces, separators)',
      'Lot code heuristic selection (length, content scoring)',
      'Weak candidate filtering (prevents false positives)',
      'Ambiguity detection (0.20 score difference threshold)',
      'User override handling when auto-detection disagrees',
    ],
  },
  {
    name: 'Scoring Engine',
    color: 'from-rose-500 to-pink-500',
    icon: Zap,
    desc: 'Weighted scoring with date validation and evidence classification',
    items: [
      'Weighted scoring: Part 60%, Date 25%, Lot 15%',
      'Logo verification bonus (+5% confidence)',
      'OCR quality modifier (penalty below 0.70 confidence)',
      'Date code validation (YYWW format, future date = instant FAKE)',
      'Evidence classification: Strong, Combined, Marginal, Weak, None',
      'Verdicts: GENUINE (≥85%), UNCERTAIN (50-84%), FAKE (<50%)',
      'Manufacturing date range checking (20+ year flag)',
      'Strong evidence bonus (part + logo + high OCR)',
    ],
  },
  {
    name: 'AI Agent Layer',
    color: 'from-indigo-500 to-blue-600',
    icon: Brain,
    desc: 'LLM-powered analysis via Groq API for human-readable verdict explanation',
    items: [
      'Groq API integration (Llama 3.3 70B Versatile)',
      'Structured JSON output with risk assessment',
      'Natural language verdict explanation',
      'Risk factor identification and classification',
      'Operator-friendly recommendations',
      'AI-powered regex pattern generation for new ICs',
      'Configurable model selection via environment',
      'Graceful degradation when AI unavailable',
    ],
  },
  {
    name: 'Knowledge Base',
    color: 'from-emerald-500 to-green-600',
    icon: Database,
    desc: 'File-based IC pattern database with Mouser API enrichment',
    items: [
      '27+ IC entries (STM32, ATmega, INA, OSD, Winbond)',
      'OCR-tolerant regex patterns per IC (part, date, lot)',
      'Schema validation with regex compilation check',
      'Aho-Corasick trie index for fast multi-pattern search',
      'Hot-reload via admin endpoint (no restart needed)',
      'Mouser Search API integration for auto-enrichment',
      'AI-assisted pattern generation for new ICs',
      'Stateless design — no database dependency',
    ],
  },
];

export default function Architecture() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-10 space-y-12">
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-500/10 text-primary-600 dark:text-primary-400 text-sm font-medium border border-primary-500/20">
          <Layers className="w-4 h-4" />
          System Architecture
        </div>
        <h1 className="text-4xl font-black text-gray-900 dark:text-white">
          <span className="gradient-text">SiliconSeal</span> Architecture
        </h1>
        <p className="text-lg text-gray-500 dark:text-gray-400 max-w-3xl mx-auto">
          Multi-layered automated optical inspection system combining computer vision, NLP algorithms,
          and AI agents for IC marking verification and counterfeit detection.
          Built for <strong className="text-primary-600 dark:text-primary-400">BEL India</strong> — SIH 2025 Problem Statement 25162.
        </p>
      </div>

      {/* Pipeline Flow */}
      <div className="flex flex-wrap items-center justify-center gap-2 text-sm">
        {[
          { icon: Upload, label: 'Image Input' },
          { icon: Eye, label: 'YOLO' },
          { icon: ScanLine, label: 'OCR' },
          { icon: Cpu, label: 'Verify' },
          { icon: Zap, label: 'Score' },
          { icon: Brain, label: 'AI Agent' },
          { icon: Shield, label: 'Verdict' },
        ].map(({ icon: Icon, label }, i) => (
          <div key={label} className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm">
              <Icon className="w-4 h-4 text-primary-500" />
              <span className="font-medium text-gray-700 dark:text-gray-300">{label}</span>
            </div>
            {i < 6 && <span className="text-gray-400 dark:text-gray-600 font-bold">→</span>}
          </div>
        ))}
      </div>

      {/* Layer Cards */}
      <div className="space-y-6">
        {LAYERS.map(({ name, color, icon: Icon, desc, items }, idx) => (
          <div key={name} className="rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden bg-white dark:bg-gray-800/50 hover:shadow-lg transition-shadow">
            <div className={`bg-gradient-to-r ${color} px-6 py-4 flex items-center gap-3`}>
              <div className="p-2 rounded-lg bg-white/20">
                <Icon className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="text-xs font-medium text-white/70 uppercase tracking-wider">Layer {String(idx + 1).padStart(2, '0')}</div>
                <h3 className="text-xl font-bold text-white">{name}</h3>
              </div>
            </div>
            <div className="p-6">
              <p className="text-gray-600 dark:text-gray-300 mb-4">{desc}</p>
              <div className="grid sm:grid-cols-2 gap-2">
                {items.map((item) => (
                  <div key={item} className="flex items-start gap-2 text-sm">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary-500 mt-1.5 shrink-0" />
                    <span className="text-gray-600 dark:text-gray-400">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Scan Modes */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white text-center">Scanning Modes</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { icon: Upload, title: 'Single Scan', desc: 'Upload one IC image for detailed verification with optional AI analysis.' },
            { icon: Camera, title: 'Live Camera', desc: 'Real-time camera capture for field inspections. Point and scan instantly.' },
            { icon: Layers, title: 'Batch Scan', desc: 'Upload up to 20 images for parallel bulk verification with per-file results.' },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="p-6 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 text-center">
              <Icon className="w-10 h-10 text-primary-500 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{title}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Security */}
      <div className="p-8 rounded-2xl bg-gradient-to-r from-primary-500/5 via-accent-500/5 to-primary-500/5 border border-primary-500/10">
        <div className="flex items-center gap-3 mb-4">
          <Lock className="w-8 h-8 text-primary-500" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Security Architecture</h2>
        </div>
        <div className="grid sm:grid-cols-2 gap-4 text-sm">
          {[
            'JWT Bearer token authentication for admin endpoints',
            'bcrypt password hashing (no plaintext storage)',
            'CORS whitelist (configurable, not wildcard)',
            'File upload size limits (10MB per file)',
            'Batch file count limits (20 files max)',
            'Base64 input validation and size checking',
            'Environment-based secrets (never in code)',
            'OAuth2 password flow with token expiration',
          ].map((item) => (
            <div key={item} className="flex items-start gap-2">
              <Shield className="w-4 h-4 text-primary-500 mt-0.5 shrink-0" />
              <span className="text-gray-600 dark:text-gray-400">{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Credits */}
      <div className="text-center p-6 rounded-xl bg-gray-50 dark:bg-gray-800/30 border border-gray-200 dark:border-gray-700">
        <Code className="w-8 h-8 text-gray-400 mx-auto mb-3" />
        <h3 className="font-bold text-gray-900 dark:text-white mb-1">Smart India Hackathon 2025 — Finalist</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">Problem Statement ID: 25162 | Organization: Bharat Electronics Limited (BEL)</p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Built by NextGen Coders 1</p>
      </div>
    </div>
  );
}
