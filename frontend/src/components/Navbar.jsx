import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import DarkModeToggle from "./DarkModeToggle";
import { useLanguage } from "../context/LanguageContext";

const base =
  "px-3 py-1 rounded-md text-xs sm:text-sm font-medium transition-colors";
const inactive = "text-gray-200 hover:bg-gray-700 hover:text-white";
const active = "bg-belBlue text-white";

function Navbar() {
  const navigate = useNavigate();
  const { lang, setLang, t } = useLanguage();

  return (
    <nav className="bg-gray-900 text-white shadow">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
        {/* Logo / Title */}
        <div
          className="font-semibold text-sm sm:text-lg tracking-wide cursor-pointer flex items-center gap-2"
          onClick={() => navigate("/")}
        >
          <span className="w-2 h-6 bg-belBlue rounded-sm" />
          <span>BEL AOI IC Verification</span>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {/* Desktop nav links */}
          <div className="hidden md:flex gap-1 sm:gap-2">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `${base} ${isActive ? active : inactive}`
              }
            >
              {t("nav.home")}
            </NavLink>
            <NavLink
              to="/scan"
              className={({ isActive }) =>
                `${base} ${isActive ? active : inactive}`
              }
            >
              {t("nav.scan")}
            </NavLink>
            <NavLink
              to="/scan/batch"
              className={({ isActive }) =>
                `${base} ${isActive ? active : inactive}`
              }
            >
              {t("nav.batch")}
            </NavLink>
            <NavLink
              to="/scan/live"
              className={({ isActive }) =>
                `${base} ${isActive ? active : inactive}`
              }
            >
              {t("nav.live")}
            </NavLink>
            <NavLink
              to="/admin/dashboard"
              className={({ isActive }) =>
                `${base} ${isActive ? active : inactive}`
              }
            >
              {t("nav.admin")}
            </NavLink>
          </div>

          {/* Language Switch */}
          <div className="flex items-center gap-1 text-xs sm:text-sm">
            <button
              onClick={() => setLang("en")}
              className={`px-2 py-1 rounded ${
                lang === "en" ? "bg-belBlue" : "bg-gray-700"
              }`}
            >
              EN
            </button>
            <button
              onClick={() => setLang("hi")}
              className={`px-2 py-1 rounded ${
                lang === "hi" ? "bg-belBlue" : "bg-gray-700"
              }`}
            >
              HI
            </button>
            <button
              onClick={() => setLang("kn")}
              className={`px-2 py-1 rounded ${
                lang === "kn" ? "bg-belBlue" : "bg-gray-700"
              }`}
            >
              KN
            </button>
          </div>

          {/* Dark mode toggle */}
          <DarkModeToggle />

          {/* Login button */}
          <button
            type="button"
            onClick={() => navigate("/admin/login")}
            className="px-3 py-1 rounded-md bg-belBlue text-xs sm:text-sm font-medium hover:bg-belBlueLight transition-colors"
          >
            {t("nav.login")}
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
