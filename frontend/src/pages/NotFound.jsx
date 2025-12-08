import React from "react";
import { Link } from "react-router-dom";

function NotFound() {
  return (
    <section className="text-center mt-16">
      <h1 className="text-3xl font-bold mb-2">404</h1>
      <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
        The page you are looking for does not exist.
      </p>
      <Link
        to="/"
        className="inline-block px-4 py-2 rounded-md bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-transform transform hover:-translate-y-0.5"
      >
        Go back Home
      </Link>
    </section>
  );
}

export default NotFound;
