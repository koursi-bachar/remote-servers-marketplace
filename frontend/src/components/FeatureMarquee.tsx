import React from 'react';
import { motion } from 'framer-motion';
import { FeatureCard } from './FeatureCard';

interface FeatureMarqueeProps {
  features: Array<{
    icon: string;
    title: string;
    description: string;
    color: 'blue' | 'emerald' | 'teal' | 'cyan' | 'violet' | 'orange';
  }>;
}

export const FeatureMarquee: React.FC<FeatureMarqueeProps> = ({ features }) => {
  const duplicatedFeatures = [...features, ...features];

  return (
    <div className="relative flex overflow-hidden group">
      <motion.div
        className="animate-marquee-right flex gap-6 px-3"
        animate={{ x: ['0%', '-50%'] }}
        transition={{
          repeat: Infinity,
          duration: 30,
          ease: 'linear'
        }}
      >
        {duplicatedFeatures.map((feature, index) => (
          <div key={index} className="flex-shrink-0">
            <FeatureCard {...feature} />
          </div>
        ))}
      </motion.div>
    </div>
  );
};