import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function AdminLogin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();

    // For now: accept every email & password
    localStorage.setItem("bel_admin_email", email || "admin@example.com");
    localStorage.setItem("bel_role", "admin");

    navigate("/admin/dashboard");
  };

  return (
    <section className="max-w-sm mx-auto mt-6">
      <h1 className="text-2xl font-bold mb-4">Admin Login</h1>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 bg-white dark:bg-gray-800 rounded-lg shadow p-4"
      >
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            type="email"
            value={email}
            required
            onChange={(e) => setEmail(e.target.value)}
            className="w-full text-sm border border-gray-300 rounded-md px-2 py-1.5 bg-white dark:bg-gray-900 dark:border-gray-700"
            placeholder="admin@bel.in (any email for now)"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <input
            type="password"
            value={password}
            required
            onChange={(e) => setPassword(e.target.value)}
            className="w-full text-sm border border-gray-300 rounded-md px-2 py-1.5 bg-white dark:bg-gray-900 dark:border-gray-700"
            placeholder="any password"
          />
        </div>

        <button
          type="submit"
          className="w-full px-4 py-2 rounded-md bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-transform transform hover:-translate-y-0.5"
        >
          Login (UI only)
        </button>

        <p className="text-xs text-gray-500 mt-1">
          Note: Authentication is UI-only for this phase. Any email/password is
          accepted.
        </p>
      </form>
    </section>
  );
}

export default AdminLogin;
