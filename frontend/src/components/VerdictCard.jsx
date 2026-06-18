import { ShieldCheck, ShieldAlert, ShieldQuestion, AlertTriangle } from 'lucide-react';

const VERDICT_CONFIG = {
  GENUINE: { icon: ShieldCheck, color: 'text-green-500', bg: 'bg-green-50 dark:bg-green-500/10', border: 'border-green-200 dark:border-green-500/20', label: 'Genuine' },
  FAKE: { icon: ShieldAlert, color: 'text-red-500', bg: 'bg-red-50 dark:bg-red-500/10', border: 'border-red-200 dark:border-red-500/20', label: 'Counterfeit Detected' },
  UNCERTAIN: { icon: ShieldQuestion, color: 'text-yellow-500', bg: 'bg-yellow-50 dark:bg-yellow-500/10', border: 'border-yellow-200 dark:border-yellow-500/20', label: 'Uncertain' },
  MULTIPLE_CANDIDATES: { icon: AlertTriangle, color: 'text-orange-500', bg: 'bg-orange-50 dark:bg-orange-500/10', border: 'border-orange-200 dark:border-orange-500/20', label: 'Multiple Matches' },
  ERROR: { icon: AlertTriangle, color: 'text-gray-500', bg: 'bg-gray-50 dark:bg-gray-500/10', border: 'border-gray-200 dark:border-gray-500/20', label: 'Error' },
};

export default function VerdictCard({ result }) {
  const cfg = VERDICT_CONFIG[result.verdict] || VERDICT_CONFIG.ERROR;
  const Icon = cfg.icon;
  const pct = Math.round((result.confidence_score || 0) * 100);

  return (
    <div className={`rounded-xl border ${cfg.border} ${cfg.bg} p-6 space-y-4`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Icon className={`w-10 h-10 ${cfg.color}`} />
          <div>
            <h3 className={`text-2xl font-bold ${cfg.color}`}>{cfg.label}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">Confidence: {pct}%</p>
          </div>
        </div>
        <div className="text-right">
          <div className={`text-3xl font-bold font-mono ${cfg.color}`}>{pct}%</div>
          <div className="text-xs text-gray-400">{result.algorithm_used}</div>
        </div>
      </div>

      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div className={`h-2 rounded-full transition-all duration-700 ${
          pct >= 85 ? 'bg-green-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-red-500'
        }`} style={{ width: `${pct}%` }} />
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {Object.entries(result.matches || {}).map(([key, val]) => (
          <div key={key} className={`text-center p-2 rounded-lg ${val ? 'bg-green-100 dark:bg-green-500/10' : 'bg-red-100 dark:bg-red-500/10'}`}>
            <div className={`text-lg ${val ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
              {val ? '✓' : '✗'}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {key.replace(/_match$/, '').replace(/_/g, ' ')}
            </div>
          </div>
        ))}
      </div>

      {result.extracted_fields && Object.keys(result.extracted_fields).length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Extracted Fields</h4>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(result.extracted_fields).filter(([k]) => k !== 'date_validation').map(([k, v]) => (
              <div key={k} className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5">
                <div className="text-xs text-gray-400">{k.replace(/_/g, ' ')}</div>
                <div className="font-mono text-sm font-medium text-gray-800 dark:text-gray-200 truncate">
                  {v || '—'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.oem_info && result.oem_info.oem && (
        <div className="px-4 py-3 rounded-lg bg-white/50 dark:bg-white/5">
          <div className="text-xs text-gray-400 mb-1">Manufacturer</div>
          <div className="font-semibold text-gray-800 dark:text-gray-200">{result.oem_info.oem}</div>
          <div className="text-sm text-gray-500">{result.oem_info.part_number} — {result.oem_info.package}</div>
        </div>
      )}

      {result.flags?.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {result.flags.map((f, i) => (
            <span key={i} className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-white/5 text-gray-600 dark:text-gray-400">
              {f}
            </span>
          ))}
        </div>
      )}

      {result.ai_analysis && !result.ai_analysis.error && (
        <div className="mt-4 p-4 rounded-lg border border-accent-500/20 bg-accent-500/5">
          <h4 className="text-sm font-semibold text-accent-600 dark:text-accent-400 mb-2 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-accent-500 animate-pulse" />
            AI Analysis
            <span className="text-xs font-normal text-gray-400 ml-auto">{result.ai_analysis.ai_model}</span>
          </h4>
          <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">{result.ai_analysis.explanation}</p>
          {result.ai_analysis.risk_factors?.length > 0 && (
            <div className="mb-2">
              <div className="text-xs font-medium text-gray-500 mb-1">Risk Factors</div>
              <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-0.5">
                {result.ai_analysis.risk_factors.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}
          {result.ai_analysis.recommendations?.length > 0 && (
            <div>
              <div className="text-xs font-medium text-gray-500 mb-1">Recommendations</div>
              <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-0.5">
                {result.ai_analysis.recommendations.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}
          <div className="mt-2 flex gap-2">
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
              result.ai_analysis.risk_level === 'LOW' ? 'bg-green-100 dark:bg-green-500/10 text-green-600' :
              result.ai_analysis.risk_level === 'MEDIUM' ? 'bg-yellow-100 dark:bg-yellow-500/10 text-yellow-600' :
              'bg-red-100 dark:bg-red-500/10 text-red-600'
            }`}>
              Risk: {result.ai_analysis.risk_level}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
