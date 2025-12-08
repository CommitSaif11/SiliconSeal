import React from "react";
import { useTheme } from "../context/ThemeContext";

export default function DarkModeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`
        relative inline-flex h-6 w-12 items-center rounded-full transition 
        ${theme === "dark" ? "bg-belBlue" : "bg-gray-500"}
      `}
    >
      <span
        className={`
          inline-block h-5 w-5 transform rounded-full bg-white shadow transition 
          ${theme === "dark" ? "translate-x-6" : "translate-x-1"}
        `}
      />
    </button>
  );
}
