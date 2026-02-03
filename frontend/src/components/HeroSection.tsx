import React from 'react';
import { motion } from 'framer-motion';

export const HeroSection: React.FC = () => {
  return (
    <section className="max-w-3xl mx-auto text-center px-6 py-20">
      {/* Main Heading */}
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="text-5xl md:text-7xl font-semibold text-gray-900 dark:text-white tracking-tighter mb-6 leading-[1.1]"
      >
        High-Performance Compute,
        <br />
        <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          On Demand.
        </span>
      </motion.h1>

      {/* CTA Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="flex flex-col sm:flex-row items-center justify-center gap-4"
      >
        <motion.a
          href="/listings"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="group relative rounded-lg p-[1px] bg-gradient-to-r from-blue-600 to-purple-600 overflow-hidden"
        >
          <div className="relative rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-3 flex items-center gap-2">
            <span className="text-sm font-bold text-white tracking-tight">
              Browse Listings
            </span>
            <motion.svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="w-4 h-4 text-white/90 group-hover:translate-x-1 transition-transform stroke-2"
            >
              <path d="M5 12h14" />
              <path d="m12 5 7 7-7 7" />
            </motion.svg>
          </div>
        </motion.a>

        <a 
          href="/signup"
          className="group inline-flex items-center justify-center px-8 py-3 text-sm font-semibold text-blue-700 dark:text-blue-200 bg-blue-50 dark:bg-blue-900/50 border-2 border-blue-200 dark:border-blue-700 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900 transition-all duration-300 transform hover:scale-105"
        >
          Become a Provider
        </a>
      </motion.div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="mt-16 grid grid-cols-3 gap-8 max-w-md mx-auto"
      >
        {[
          { value: '100+', label: 'GPU Models' },
          { value: '99.9%', label: 'Uptime' },
          { value: '24/7', label: 'Support' },
        ].map((stat, index) => (
          <div key={stat.label} className="text-center">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {stat.value}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {stat.label}
            </div>
          </div>
        ))}
      </motion.div>
    </section>
  );
};