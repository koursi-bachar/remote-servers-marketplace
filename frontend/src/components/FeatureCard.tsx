import React from 'react';
import { motion } from 'framer-motion';

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
  color: 'blue' | 'emerald' | 'teal' | 'cyan' | 'violet' | 'orange';
}

const colorClasses = {
  blue: {
    bg: 'bg-blue-100 dark:bg-blue-500/10',
    text: 'text-blue-600 dark:text-blue-400',
    border: 'hover:border-blue-300 dark:hover:border-blue-500/30'
  },
  emerald: {
    bg: 'bg-emerald-100 dark:bg-emerald-500/10',
    text: 'text-emerald-600 dark:text-emerald-400',
    border: 'hover:border-emerald-300 dark:hover:border-emerald-500/30'
  },
  teal: {
    bg: 'bg-teal-100 dark:bg-teal-500/10',
    text: 'text-teal-600 dark:text-teal-400',
    border: 'hover:border-teal-300 dark:hover:border-teal-500/30'
  },
  cyan: {
    bg: 'bg-cyan-100 dark:bg-cyan-500/10',
    text: 'text-cyan-600 dark:text-cyan-400',
    border: 'hover:border-cyan-300 dark:hover:border-cyan-500/30'
  },
  violet: {
    bg: 'bg-violet-100 dark:bg-violet-500/10',
    text: 'text-violet-600 dark:text-violet-400',
    border: 'hover:border-violet-300 dark:hover:border-violet-500/30'
  },
  orange: {
    bg: 'bg-orange-100 dark:bg-orange-500/10',
    text: 'text-orange-600 dark:text-orange-400',
    border: 'hover:border-orange-300 dark:hover:border-orange-500/30'
  }
};

export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  description,
  color
}) => {
  const colors = colorClasses[color];

  return (
    <motion.div
      whileHover={{ y: -5 }}
      className={`p-6 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 ${colors.border} transition-all shadow-sm hover:shadow-lg`}
    >
      <div className="flex items-center gap-3 mb-4">
        <div className={`w-8 h-8 rounded-lg ${colors.bg} flex items-center justify-center ${colors.text}`}>
          <span className="text-xl">{icon}</span>
        </div>
        <div className="text-sm font-semibold text-zinc-900 dark:text-white">
          {title}
        </div>
      </div>
      <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
        {description}
      </p>
    </motion.div>
  );
};