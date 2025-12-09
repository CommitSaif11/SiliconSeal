import React from "react";
import { Link } from "react-router-dom";
import { useTheme } from "../context/ThemeContext";
import { useLanguage } from "../context/LanguageContext";

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();
  const { lang, setLang, t } = useLanguage();

  return (
    <nav className="bg-white dark:bg-gray-800 px-6 py-3 shadow-lg flex justify-between items-center border-b border-gray-300 dark:border-gray-700">
      <Link to="/" className="text-2xl font-bold text-[var(--bel-blue)]">
        BEL AOI
      </Link>

      <div className="flex items-center gap-4">

        {/* Language Switch */}
        <select
          value={lang}
          onChange={(e) => setLang(e.target.value)}
          className="input w-auto"
        >
          <option value="en">EN</option>
          <option value="hi">हिंदी</option>
          <option value="kn">ಕನ್ನಡ</option>
        </select>

        {/* Theme switch */}
        <button onClick={toggleTheme} className="btn-secondary">
          {theme === "light" ? "Dark" : "Light"}
        </button>

        {/* Admin Button */}
        <Link to="/admin/login" className="btn-primary">
          Admin
        </Link>
      </div>
    </nav>
  );
}
