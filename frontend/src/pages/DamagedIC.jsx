// src/pages/DamagedIC.jsx
import React, { useState } from "react";

export default function DamagedIC() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");

  const handleFile = (e) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setPreview(URL.createObjectURL(f));
    }
  };

  return (
    <section>
      <h1 className="page-title">Damaged IC Inspection</h1>
      <p className="text-sm text-gray-400 mb-6">
        Upload an IC image where the marking is partially damaged or unclear.
        Select the expected IC model to compare OCR results and marking clues.
      </p>

      {/* Upload Section */}
      <div className="card mb-6">
        <h2 className="section-title">Upload Damaged IC Image</h2>

        <input
          type="file"
          accept="image/*"
          onChange={handleFile}
          className="file-input w-full"
        />

        {preview && (
          <img
            src={preview}
            alt="preview"
            className="w-40 mt-4 rounded border dark:border-gray-700"
          />
        )}

        {/* Model selection */}
        <div className="mt-4">
          <label className="text-sm font-medium">Expected IC Model</label>
          <select className="input mt-1">
            <option>STM32F030C8T6 (STMicroelectronics)</option>
            <option>ATMEGA328P (Microchip)</option>
            <option>SN74HC595 (Texas Instruments)</option>
            <option>TPS7A4700 (Texas Instruments)</option>
            <option>STM32H743II (STMicroelectronics)</option>
          </select>
        </div>
      </div>

      {/* Reference Information */}
      <div className="card mb-6">
        <h2 className="section-title">Reference Marking Information</h2>

        <p className="text-sm">
          <b>Part:</b> STM32F030C8T6 (STMicroelectronics)
        </p>
        <p className="text-sm">
          <b>Package:</b> LQFP-48
        </p>

        <div className="mt-4">
          <h3 className="text-sm font-semibold">Typical Marking</h3>

          <div className="bg-gray-900 p-3 rounded text-xs mt-1">
            STM32F030<br />
            C8T6<br />
            B123
          </div>
        </div>

        <p className="text-[11px] text-gray-500 mt-2">
          *Used for AI comparison against your uploaded damaged IC image.*
        </p>
      </div>

      {/* ================================
          Damage Inspection Result Summary
         ================================ */}
      <div className="card mt-6">
        <h2 className="section-title">Damage Inspection Summary</h2>
        <p className="text-xs text-gray-400 mb-3">
          Summary of marking interpretation and comparison based on OCR analysis.
        </p>

        <div className="space-y-3 text-sm">

          {/* Record ID */}
          <div>
            <div className="font-semibold">Record ID</div>
            <div className="bg-gray-800 p-2 rounded text-xs text-gray-300">
              692874efff4418f365cab2cc
            </div>
            <p className="text-[11px] text-gray-500 mt-1">
              Internal reference identifier for this inspection record.
            </p>
          </div>

          {/* Timestamp */}
          <div>
            <div className="font-semibold">Timestamp</div>
            <div className="bg-gray-800 p-2 rounded text-xs text-gray-300">
              2025-11-27 15:57:35 UTC
            </div>
            <p className="text-[11px] text-gray-500 mt-1">
              Time when the damaged IC image was processed.
            </p>
          </div>

          {/* Part ID */}
          <div>
            <div className="font-semibold">Part ID</div>
            <div className="bg-gray-800 p-2 rounded text-xs text-gray-300">
              STM32F030C8T6
            </div>
            <p className="text-[11px] text-gray-500 mt-1">
              Expected IC model used for comparison.
            </p>
          </div>

          {/* Algorithm */}
          <div>
            <div className="font-semibold">Algorithm Used</div>
            <div className="bg-gray-800 p-2 rounded text-xs text-gray-300">
              Regex
            </div>
            <p className="text-[11px] text-gray-500 mt-1">
              Pattern-matching technique applied during OCR evaluation.
            </p>
          </div>

          {/* OCR Text */}
          <div>
            <div className="font-semibold">OCR Extracted Text</div>
            <div className="bg-gray-800 p-2 rounded text-xs text-gray-300">
              TII12 C TJ TJ IT JT JUZ 12 TIIZ C TJ TJ IT JT JUZ
            </div>
            <p className="text-[11px] text-gray-500 mt-1">
              Raw marking interpreted from the damaged IC surface.
            </p>
          </div>

          {/* Confidence */}
          <div>
            <div className="font-semibold">Confidence Score</div>
            <div className="text-blue-400 text-xl">0.15</div>
            <p className="text-[11px] text-gray-500 mt-1">
              Low score indicates uncertainty due to distortion or unclear marking.
            </p>
          </div>

          {/* Verdict */}
          <div>
            <div className="font-semibold">Automated Verdict</div>
            <div className="text-yellow-400 text-lg font-bold">UNCERTAIN</div>
            <p className="text-[11px] text-gray-500 mt-1">
              The system could not confidently match the marking with reference data.
            </p>
          </div>

          {/* Flags */}
          <div>
            <div className="font-semibold">Flags</div>
            <div className="bg-gray-800 p-2 rounded text-xs text-gray-300">
              • low_marking_clarity<br />
              • inconsistent_line_structure
            </div>
            <p className="text-[11px] text-gray-500 mt-1">
              Indicators that signal degradation or unclear surface patterns.
            </p>
          </div>

          {/* Admin Review */}
          <div>
            <div className="font-semibold">Admin Review Required</div>
            <div className="text-green-400 text-lg font-bold">No</div>
            <p className="text-[11px] text-gray-500 mt-1">
              This inspection did not require manual review.
            </p>
          </div>

        </div>
      </div>
    </section>
  );
}
