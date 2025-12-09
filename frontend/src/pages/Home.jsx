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
    <section>

      {/* Hero Section */}
      <div className="rounded-2xl bg-gradient-to-r from-[var(--bel-blue)] to-[var(--bel-blue-light)] text-white p-8 shadow-xl flex flex-col md:flex-row gap-6 justify-between mt-4">

        <div className="md:w-2/3">
          <h1 className="text-4xl font-bold mb-3">{t("home.title")}</h1>
          <p className="text-white/90 text-base max-w-xl">{t("home.subtitle")}</p>

          <div className="mt-6 flex flex-wrap gap-4">
            <Link to="/scan" className="btn-secondary bg-white text-[var(--bel-blue)] font-semibold">
              {t("home.startScan")}
            </Link>

            <Link to="/admin/dashboard" className="btn-secondary border-white text-white hover:bg-white/20">
              {t("home.adminDashboard")}
            </Link>
          </div>
        </div>

        {/* Status Card */}
        <div className="md:w-1/3 bg-white/10 rounded-xl p-4">
          <h2 className="font-semibold">{t("home.systemStatus")}</h2>
          <p className="text-green-200 text-sm">{statusText}</p>
          <p className="mt-3 text-xs text-blue-100">{t("home.backend")}</p>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
        <FeatureCard title={t("home.singleScanTitle")} desc={t("home.singleScanDesc")} link="/scan" t={t} />
        <FeatureCard title={t("home.batchScanTitle")} desc={t("home.batchScanDesc")} link="/scan/batch" t={t} />
        
      </div>
    </section>
  );
}

function FeatureCard({ title, desc, link, t }) {
  return (
    <Link to={link} className="card hover:shadow-xl transition-all">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-700 dark:text-gray-300">{desc}</p>
      <button className="btn-primary mt-4 text-xs">{t("home.open")}</button>
    </Link>
  );
}
