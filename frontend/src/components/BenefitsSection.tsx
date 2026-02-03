import React from 'react';
import { motion } from 'framer-motion';
import { FeatureCard } from './FeatureCard';
import { FeatureMarquee } from './FeatureMarquee';

// Define a type for the color to match FeatureCard expectations
type BenefitColor = 'blue' | 'emerald' | 'teal' | 'cyan' | 'violet' | 'orange';

interface Benefit {
  icon: string;
  title: string;
  description: string;
  color: BenefitColor;
}

const benefits: Benefit[] = [ // Added explicit typing
  {
    icon: '⚡',
    title: 'Lightning Fast',
    description: 'Deploy GPU instances in under 60 seconds',
    color: 'blue' as const // Use 'as const' for literal type
  },
  {
    icon: '🔒',
    title: 'Enterprise Security',
    description: 'Military-grade encryption and isolated VPCs',
    color: 'emerald' as const
  },
  {
    icon: '📊',
    title: 'Real-time Analytics',
    description: 'Monitor performance, usage, and costs',
    color: 'teal' as const
  },
  {
    icon: '🔄',
    title: 'Auto Scaling',
    description: 'Automatically scale based on workload',
    color: 'cyan' as const
  },
  {
    icon: '💰',
    title: 'Cost Optimized',
    description: 'Spot instances and reserved pricing',
    color: 'violet' as const
  },
  {
    icon: '🌐',
    title: 'Global Network',
    description: 'Deploy in 15+ regions worldwide',
    color: 'orange' as const
  }
];

export const BenefitsSection: React.FC = () => {
  return (
    <section className="py-12 relative overflow-hidden bg-transparent">
      <div className="max-w-7xl mx-auto px-6 mb-12 text-center">
        <h2 className="text-3xl md:text-4xl font-semibold tracking-tighter text-gray-900 dark:text-white mb-4">
          Why Choose Our Platform
        </h2>
        <p className="text-gray-600 dark:text-gray-300">
          Experience the advantages of modern GPU compute
        </p>
      </div>

      {/* Feature Marquee */}
      <FeatureMarquee features={benefits} />

      {/* Static Benefit Cards */}
      <div className="mt-12 max-w-6xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {benefits.slice(0, 3).map((benefit, index) => (
            <motion.div
              key={benefit.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <FeatureCard {...benefit} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};