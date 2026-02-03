import React, { useEffect, useState } from 'react';
import { motion, useAnimation } from 'framer-motion';
import { useInView } from 'react-intersection-observer';

export const HomepageShowcase: React.FC = () => {
  const controls = useAnimation();
  const [ref, inView] = useInView();
  
  useEffect(() => {
    if (inView) {
      controls.start('visible');
    }
  }, [controls, inView]);

  return (
    <section className="py-12 px-4 max-w-7xl mx-auto">
      <div className="text-center mb-12">
        <motion.h2 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-3xl font-bold text-gray-900 dark:text-white mb-4"
        >
          Why Choose Our Platform?
        </motion.h2>
        <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Discover the advantages of our modern server marketplace
        </p>
      </div>

      {/* Animated Stats Counter */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
        <StatCard endValue={100} label="Active Servers" suffix="+" duration={2} />
        <StatCard endValue={99.9} label="Uptime" suffix="%" duration={2.5} />
        <StatCard endValue={24} label="Support" suffix="/7" duration={3} />
        <StatCard endValue={50} label="Countries" suffix="+" duration={2.2} />
      </div>

      {/* Interactive Feature Cards */}
      <div ref={ref} className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <FeatureCard 
          icon="⚡"
          title="Lightning Fast"
          description="Deploy servers in under 60 seconds with our automated provisioning system."
          delay={0}
        />
        <FeatureCard 
          icon="🔒"
          title="Enterprise Security"
          description="Military-grade encryption and isolated environments for every deployment."
          delay={0.2}
        />
        <FeatureCard 
          icon="📊"
          title="Real-time Analytics"
          description="Monitor performance, usage, and costs with our comprehensive dashboard."
          delay={0.4}
        />
      </div>

      {/* Animated CTA */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-16 text-center"
      >
        <div className="inline-block p-1 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl shadow-lg">
          <button 
            onClick={() => window.location.href = '/signup'}
            className="px-8 py-4 bg-white dark:bg-gray-900 text-gray-900 dark:text-white rounded-xl font-bold text-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-all transform hover:scale-105"
          >
            Start Your Free Trial →
          </button>
        </div>
      </motion.div>
    </section>
  );
};

// Stat Counter Component
const StatCard: React.FC<{ endValue: number; label: string; suffix: string; duration: number }> = ({ 
  endValue, label, suffix, duration 
}) => {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let start = 0;
    const increment = endValue / (duration * 60);
    const timer = setInterval(() => {
      start += increment;
      if (start >= endValue) {
        setCount(endValue);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 1000 / 60);
    
    return () => clearInterval(timer);
  }, [endValue, duration]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-center p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
    >
      <div className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
        {count.toFixed(endValue % 1 === 0 ? 0 : 1)}{suffix}
      </div>
      <div className="text-gray-600 dark:text-gray-300">{label}</div>
    </motion.div>
  );
};

// Feature Card Component
const FeatureCard: React.FC<{ icon: string; title: string; description: string; delay: number }> = ({ 
  icon, title, description, delay 
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      whileHover={{ y: -5 }}
      className="p-6 bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 rounded-xl shadow-lg hover:shadow-xl border border-gray-200 dark:border-gray-700 transition-all"
    >
      <div className="text-5xl mb-4">{icon}</div>
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">{title}</h3>
      <p className="text-gray-600 dark:text-gray-300">{description}</p>
    </motion.div>
  );
};