import React from 'react';
import { motion } from 'framer-motion';
import { HeroSection } from './HeroSection';
import { BenefitsSection } from './BenefitsSection'; // Renamed from FeaturesSection
import { DashboardPreview } from './DashboardPreview';
import { TestimonialsSection } from './TestimonialsSection';
import { useScrollAnimation } from '../hooks/useScrollAnimation';

export const HomePage: React.FC = () => {
  const { ref: benefitsRef, controls: benefitsControls } = useScrollAnimation(0.1); // Lower threshold
  const { ref: dashboardRef, controls: dashboardControls } = useScrollAnimation(0.1); // Lower threshold
  const { ref: testimonialsRef, controls: testimonialsControls } = useScrollAnimation(0.1); // Lower threshold

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-300">
      <main className="relative z-10 overflow-hidden">
        <div className="relative z-10">
          <HeroSection />
          
          {/* Trusted Companies Logos */}
          <section className="mt-24 border-y border-gray-200 dark:border-gray-700 py-10 overflow-hidden transition-colors duration-500">
            <div className="flex justify-center flex-wrap gap-12 md:gap-20 opacity-50 px-6 grayscale hover:grayscale-0 transition-all duration-700">
              {['NVIDIA', 'AMD', 'Intel', 'AWS', 'Google Cloud', 'Microsoft Azure'].map((company, index) => (
                <motion.div
                  key={company}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 0.5, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="text-lg font-semibold text-gray-900 dark:text-white"
                >
                  {company}
                </motion.div>
              ))}
            </div>
          </section>

          {/* Benefits Section (formerly Features) */}
          <motion.section
            ref={benefitsRef}
            animate={benefitsControls}
            initial="hidden"
            variants={{
              visible: { opacity: 1, y: 0 },
              hidden: { opacity: 0, y: 20 } // Reduced y offset for smoother animation
            }}
            id="benefits" // Changed from features
            className="py-16"
          >
            <BenefitsSection />
          </motion.section>

          {/* Dashboard Preview - no animation delay */}
          <section 
            ref={dashboardRef}
            className="py-16"
          >
            <motion.div
              animate={dashboardControls}
              initial="hidden"
              variants={{
                visible: { opacity: 1, y: 0 },
                hidden: { opacity: 0, y: 20 }
              }}
            >
              <DashboardPreview />
            </motion.div>
          </section>

          {/* Testimonials Section */}
          <motion.section
            ref={testimonialsRef}
            animate={testimonialsControls}
            initial="hidden"
            variants={{
              visible: { opacity: 1, y: 0 },
              hidden: { opacity: 0, y: 20 }
            }}
            id="testimonials"
            className="py-16"
          >
            <TestimonialsSection />
          </motion.section>
        </div>
      </main>
    </div>
  );
};