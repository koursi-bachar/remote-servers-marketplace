import React from 'react';
import { motion } from 'framer-motion';

const technologies = [
  { name: 'NVIDIA A100', icon: '🎮' },
  { name: 'AMD MI250X', icon: '⚡' },
  { name: 'Intel Xeon', icon: '💻' },
  { name: 'Ubuntu', icon: '🐧' },
  { name: 'Docker', icon: '🐳' },
  { name: 'Kubernetes', icon: '⚓' },
  { name: 'TensorFlow', icon: '🧠' },
  { name: 'PyTorch', icon: '🔥' },
  { name: 'FastAPI', icon: '🚀' },
  { name: 'PostgreSQL', icon: '🐘' },
];

export const TechStackMarquee: React.FC = () => {
  return (
    <div className="py-12 overflow-hidden">
      <div className="text-center mb-8">
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Supported Technologies
        </h3>
        <p className="text-gray-600 dark:text-gray-300">
          Run your favorite frameworks and tools
        </p>
      </div>
      
      <div className="relative">
        <motion.div
          className="flex space-x-8"
          animate={{ x: ['0%', '-50%'] }}
          transition={{ repeat: Infinity, duration: 30, ease: 'linear' }}
        >
          {[...technologies, ...technologies].map((tech, index) => (
            <div
              key={index}
              className="flex items-center space-x-3 px-6 py-3 bg-white dark:bg-gray-800 rounded-full shadow-md hover:shadow-lg transition-shadow"
            >
              <span className="text-2xl">{tech.icon}</span>
              <span className="font-semibold text-gray-800 dark:text-gray-200">{tech.name}</span>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};