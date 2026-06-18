import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Eye, ScanLine, Cpu, Zap, Brain, ShieldCheck, Camera, Layers } from 'lucide-react';

const PIPELINES = {
  scan: {
    title: 'Single IC Verification',
    subtitle: 'Upload → Detect → Read → Verify → AI Verdict',
    steps: [
      { icon: Upload, label: 'Upload Image', desc: 'Drag & drop your IC chip image' },
      { icon: Eye, label: 'YOLO Detection', desc: 'AI detects and crops the IC region' },
      { icon: ScanLine, label: 'PaddleOCR', desc: 'Multi-pass text extraction from chip' },
      { icon: Cpu, label: 'Pattern Match', desc: 'Regex / Aho-Corasick verification' },
      { icon: Zap, label: 'Scoring', desc: 'Weighted confidence calculation' },
      { icon: Brain, label: 'AI Analysis', desc: 'LLM explains the verdict in detail' },
      { icon: ShieldCheck, label: 'Verdict', desc: 'GENUINE / FAKE / UNCERTAIN' },
    ],
  },
  batch: {
    title: 'Batch Verification',
    subtitle: 'Upload Multiple → Parallel Processing → Per-File Results',
    steps: [
      { icon: Layers, label: 'Upload Batch', desc: 'Up to 20 IC images at once' },
      { icon: Eye, label: 'YOLO per Image', desc: 'Each image gets IC detection' },
      { icon: ScanLine, label: 'Parallel OCR', desc: 'All images processed concurrently' },
      { icon: Cpu, label: 'Verify Each', desc: 'Individual pattern matching' },
      { icon: Zap, label: 'Score All', desc: 'Per-file confidence scores' },
      { icon: ShieldCheck, label: 'Batch Results', desc: 'Summary with pass/fail per IC' },
    ],
  },
  live: {
    title: 'Live Camera Inspection',
    subtitle: 'Point → Capture → Instant Verification',
    steps: [
      { icon: Camera, label: 'Camera Feed', desc: 'Access device camera' },
      { icon: Upload, label: 'Capture Frame', desc: 'Snapshot sent as base64' },
      { icon: Eye, label: 'YOLO Detect', desc: 'Real-time IC localization' },
      { icon: ScanLine, label: 'OCR Read', desc: 'Extract markings from frame' },
      { icon: Cpu, label: 'Verify', desc: 'Match against knowledge base' },
      { icon: ShieldCheck, label: 'Instant Result', desc: 'Verdict in seconds' },
    ],
  },
};

export default function PipelineBanner({ mode = 'scan' }) {
  const pipeline = PIPELINES[mode];
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % pipeline.steps.length);
    }, 2500);
    return () => clearInterval(timer);
  }, [pipeline.steps.length]);

  return (
    <div className="rounded-2xl overflow-hidden border border-primary-500/20 bg-gradient-to-r from-primary-500/5 via-accent-500/5 to-primary-500/5">
      {/* Header */}
      <div className="px-5 py-3 border-b border-primary-500/10 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-primary-600 dark:text-primary-400">{pipeline.title}</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{pipeline.subtitle}</p>
        </div>
        <div className="flex items-center gap-1">
          {pipeline.steps.map((_, i) => (
            <div
              key={i}
              className={`w-1.5 h-1.5 rounded-full transition-all duration-500 ${
                i === activeStep ? 'bg-primary-500 scale-125' : i < activeStep ? 'bg-primary-300 dark:bg-primary-700' : 'bg-gray-300 dark:bg-gray-600'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Steps ticker */}
      <div className="px-5 py-3 flex items-center gap-3 overflow-hidden">
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-none pb-1">
          {pipeline.steps.map((step, i) => {
            const Icon = step.icon;
            const isActive = i === activeStep;
            const isPast = i < activeStep;
            return (
              <motion.div
                key={i}
                animate={{
                  scale: isActive ? 1.05 : 1,
                  opacity: isActive ? 1 : isPast ? 0.5 : 0.7,
                }}
                transition={{ duration: 0.4 }}
                className={`flex items-center gap-2 shrink-0 px-3 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-500/10 border border-primary-500/30'
                    : 'border border-transparent'
                }`}
              >
                <motion.div
                  animate={isActive ? { rotate: [0, -10, 10, 0] } : {}}
                  transition={{ duration: 0.5 }}
                >
                  <Icon className={`w-4 h-4 shrink-0 ${
                    isActive ? 'text-primary-500' : isPast ? 'text-green-500' : 'text-gray-400'
                  }`} />
                </motion.div>
                <div className="min-w-0">
                  <div className={`text-xs font-semibold whitespace-nowrap ${
                    isActive ? 'text-primary-600 dark:text-primary-400' : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    {step.label}
                  </div>
                  {isActive && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="text-[10px] text-gray-500 dark:text-gray-400 whitespace-nowrap"
                    >
                      {step.desc}
                    </motion.div>
                  )}
                </div>
                {i < pipeline.steps.length - 1 && (
                  <span className={`text-xs shrink-0 ml-1 ${isPast ? 'text-green-400' : 'text-gray-300 dark:text-gray-600'}`}>→</span>
                )}
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Active step highlight */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeStep}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
          className="px-5 pb-3"
        >
          <div className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-white/60 dark:bg-white/5 border border-gray-200/50 dark:border-gray-700/50">
            {(() => { const Icon = pipeline.steps[activeStep].icon; return <Icon className="w-5 h-5 text-primary-500 shrink-0" />; })()}
            <div>
              <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                Step {activeStep + 1}: {pipeline.steps[activeStep].label}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">
                — {pipeline.steps[activeStep].desc}
              </span>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
