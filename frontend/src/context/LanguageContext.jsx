import React, { createContext, useContext, useState } from "react";

const LanguageContext = createContext();

const translations = {
  en: {
    nav: {
      home: "Home",
      scan: "Scan",
      batch: "Batch",
      live: "Live",
      admin: "Admin",
      login: "Login",
    },
    home: {
      title: "BEL AOI IC Marking Verification",
      subtitle:
        "Upload IC images or connect a camera feed to automatically verify marking authenticity using OEM knowledge base and AI-powered OCR.",
      startScan: "Start Scan",
      adminDashboard: "Admin Dashboard",
      systemStatus: "System Status",
      statusOnline: "Online (UI connected to FastAPI)",
      backend: "Backend: FastAPI · MongoDB (optional) · Knowledge Base (JSON)",
      singleScanTitle: "Single Scan",
      singleScanDesc:
        "Upload a single IC image and verify OEM authenticity instantly.",
      batchScanTitle: "Batch Scan",
      batchScanDesc:
        "Upload multiple files and verify all IC markings in one batch.",
      liveScanTitle: "Live Camera Scan",
      liveScanDesc:
        "Connect a camera and perform real-time marking verification.",
      open: "Open",
    },
  },

  hi: {
    nav: {
      home: "होम",
      scan: "स्कैन",
      batch: "बैच",
      live: "लाइव",
      admin: "एडमिन",
      login: "लॉगिन",
    },
    home: {
      title: "बीईएल एओआई आईसी मार्किंग सत्यापन",
      subtitle:
        "आईसी इमेज अपलोड करें या कैमरा फीड कनेक्ट करें और OEM नॉलेज बेस तथा एआई आधारित OCR से मार्किंग सत्यापित करें।",
      startScan: "स्कैन शुरू करें",
      adminDashboard: "एडमिन डैशबोर्ड",
      systemStatus: "सिस्टम स्थिति",
      statusOnline: "ऑनलाइन (UI FastAPI से जुड़ा हुआ है)",
      backend: "बैकएंड: FastAPI · MongoDB (वैकल्पिक) · नॉलेज बेस (JSON)",
      singleScanTitle: "सिंगल स्कैन",
      singleScanDesc:
        "एक आईसी इमेज अपलोड करें और तुरंत OEM सत्यापन प्राप्त करें।",
      batchScanTitle: "बैच स्कैन",
      batchScanDesc:
        "कई फाइलें अपलोड करें और सभी आईसी मार्किंग को एक साथ सत्यापित करें।",
      liveScanTitle: "लाइव कैमरा स्कैन",
      liveScanDesc: "कैमरा कनेक्ट करें और रियल-टाइम मार्किंग सत्यापन करें।",
      open: "ओपन",
    },
  },

  kn: {
    nav: {
      home: "ಮುಖಪುಟ",
      scan: "ಸ್ಕ್ಯಾನ್",
      batch: "ಬ್ಯಾಚ್",
      live: "ಲೈವ್",
      admin: "ನಿರ್ವಹಣೆ",
      login: "ಲಾಗಿನ್",
    },
    home: {
      title: "ಬಿಇಎಲ್ AOI ಐಸಿ ಮಾರ್ಕಿಂಗ್ ಪರಿಶೀಲನೆ",
      subtitle:
        "IC ಚಿತ್ರಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕ್ಯಾಮೆರಾವನ್ನು ಕನೆಕ್ಟ್ ಮಾಡಿ, OEM ಜ್ಞಾನಕೋಶ ಮತ್ತು AI ಆಧಾರಿತ OCR ಬಳಸಿ ಮಾರ್ಕಿಂಗ್ ಪರಿಶೀಲಿಸಿ.",
      startScan: "ಸ್ಕ್ಯಾನ್ ಪ್ರಾರಂಭಿಸಿ",
      adminDashboard: "ನಿರ್ವಹಣೆ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
      systemStatus: "ಸಿಸ್ಟಮ್ ಸ್ಥಿತಿ",
      statusOnline: "ಆನ್ಲೈನ್ (UI FastAPI ಗೆ ಸಂಪರ್ಕವಾಗಿದೆ)",
      backend: "ಬ್ಯಾಕ್‌ಎಂಡ್: FastAPI · MongoDB (ಐಚ್ಛಿಕ) · ಜ್ಞಾನಕೋಶ (JSON)",
      singleScanTitle: "ಏಕ ಸ್ಕ್ಯಾನ್",
      singleScanDesc:
        "ಒಂದು IC ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಮತ್ತು OEM ಮಾನ್ಯತೆ ಪರಿಶೀಲಿಸಿ.",
      batchScanTitle: "ಬ್ಯಾಚ್ ಸ್ಕ್ಯಾನ್",
      batchScanDesc:
        "ಹಲವಾರು ಕಡತಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಮತ್ತು ಎಲ್ಲಾ IC ಮಾರ್ಕಿಂಗ್ ಪರಿಶೀಲಿಸಿ.",
      liveScanTitle: "ಲೈವ್ ಕ್ಯಾಮೆರಾ ಸ್ಕ್ಯಾನ್",
      liveScanDesc: "ಕ್ಯಾಮೆರಾವನ್ನು ಕನೆಕ್ಟ್ ಮಾಡಿ ಮತ್ತು ನೇರ ಪ್ರಸಾರದಲ್ಲಿ ಪರಿಶೀಲನೆ ಮಾಡಿ.",
      open: "ಓಪನ್",
    },
  },
};

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState("en");

  const t = (path) => {
    const parts = path.split(".");
    let obj = translations[lang];
    for (const p of parts) {
      if (!obj[p]) return path;
      obj = obj[p];
    }
    return obj;
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export const useLanguage = () => useContext(LanguageContext);
