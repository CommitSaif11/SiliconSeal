import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export default function Home() {
  const { t } = useLanguage();
  const [statusText, setStatusText] = useState("Checking...");

  useEffect(() => {
    fetch(`${API_BASE_URL}/health`)
      .then((res) => res.json())
      .then(() => setStatusText(t("home.statusOnline")))
      .catch(() => setStatusText("Offline"));
  }, [t]);

  return (
    <div>
      {/* Hero */}
      <div className="rounded-2xl bg-gradient-to-r from-belBlue to-belBlueLight text-white p-6 md:p-8 shadow-lg flex flex-col md:flex-row gap-6 justify-between">
        <div className="md:w-2/3">
          <h1 className="text-3xl md:text-4xl font-bold mb-3">
            {t("home.title")}
          </h1>
          <p className="text-sm md:text-base text-blue-100 max-w-xl">
            {t("home.subtitle")}
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link
              to="/scan"
              className="px-5 py-2.5 rounded-lg bg-white text-belBlue font-semibold text-sm hover:bg-blue-50"
            >
              {t("home.startScan")}
            </Link>
            <Link
              to="/admin/dashboard"
              className="px-5 py-2.5 rounded-lg border border-blue-100 text-sm text-white/90 hover:bg-white/10"
            >
              {t("home.adminDashboard")}
            </Link>
          </div>
        </div>

        {/* Status Card */}
        <div className="md:w-1/3 bg-white/10 rounded-xl p-4 flex flex-col justify-between">
          <div>
            <h2 className="font-semibold mb-2">{t("home.systemStatus")}</h2>
            <p className="text-green-200 text-sm">{statusText}</p>
          </div>
          <p className="mt-3 text-xs text-blue-100">
            {t("home.backend")}
          </p>
        </div>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
        <FeatureCard
          title={t("home.singleScanTitle")}
          desc={t("home.singleScanDesc")}
          link="/scan"
          t={t}
        />
        <FeatureCard
          title={t("home.batchScanTitle")}
          desc={t("home.batchScanDesc")}
          link="/scan/batch"
          t={t}
        />
        <FeatureCard
          title={t("home.liveScanTitle")}
          desc={t("home.liveScanDesc")}
          link="/scan/live"
          t={t}
        />
      </div>
    </div>
  );
}

function FeatureCard({ title, desc, link, t }) {
  return (
    <Link
      to={link}
      className="block p-5 rounded-xl bg-white dark:bg-gray-800 shadow hover:shadow-xl transition-all border border-gray-200 dark:border-gray-700"
    >
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-sm text-gray-700 dark:text-gray-300">{desc}</p>
      <button className="mt-4 px-4 py-2 bg-belBlue hover:bg-belBlueLight text-white rounded-lg text-xs">
        {t("home.open")}
      </button>
    </Link>
  );
}
