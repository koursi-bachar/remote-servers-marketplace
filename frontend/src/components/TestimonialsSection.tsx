import React from 'react';
import { motion } from 'framer-motion';

interface Testimonial {
  id: string;
  quote: string;
  author: string;
  role: string;
  company: string;
  rating: number;
  initials: string;
  gradient: string;
}

const testimonials: Testimonial[] = [
  {
    id: '1',
    quote: "Reduced our ML training costs by 60% while improving performance. The flexibility to scale GPU power on demand is revolutionary.",
    author: "Alex Chen",
    role: "AI Research Lead",
    company: "TechCorp AI",
    rating: 5,
    initials: "AC",
    gradient: "from-blue-500 to-emerald-500"
  },
  {
    id: '2',
    quote: "The easiest way to access high-end GPUs without capital expenditure. Our rendering farm runs 24/7 with perfect reliability.",
    author: "Maria Rodriguez",
    role: "CTO",
    company: "Animation Studios",
    rating: 5,
    initials: "MR",
    gradient: "from-purple-500 to-pink-500"
  },
  {
    id: '3',
    quote: "We switched from AWS and never looked back. The pricing transparency and support are unmatched in the industry.",
    author: "James Wilson",
    role: "Data Science Director",
    company: "FinTech Solutions",
    rating: 5,
    initials: "JW",
    gradient: "from-orange-500 to-red-500"
  }
];

const StarRating: React.FC<{ rating: number }> = ({ rating }) => {
  return (
    <div className="flex gap-1 mb-4">
      {[...Array(5)].map((_, i) => (
        <svg
          key={i}
          className={`w-5 h-5 ${
            i < rating
              ? 'text-yellow-400 fill-current'
              : 'text-gray-300 dark:text-gray-600 fill-current'
          }`}
          viewBox="0 0 20 20"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  );
};

export const TestimonialsSection: React.FC = () => {
  return (
    <section id="testimonials" className="py-20 bg-transparent transition-colors duration-500">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-semibold tracking-tighter text-gray-900 dark:text-white mb-6">
            Trusted by AI Teams Worldwide
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            See what our customers have to say
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.id}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="group relative p-8 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl transition-all duration-300 flex flex-col h-full min-h-[300px]"
            >
              {/* Star Rating */}
              <div className="mb-4">
                <StarRating rating={testimonial.rating} />
              </div>
              
              {/* Quote - Flex-grow to push content down and center vertically */}
              <div className="flex-grow flex flex-col justify-center mb-6">
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed italic text-center md:text-left">
                  "{testimonial.quote}"
                </p>
              </div>
              
              {/* Author Info - Fixed at bottom with proper spacing */}
              <div className="pt-4 border-t border-gray-100 dark:border-gray-700 mt-auto">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${testimonial.gradient} flex items-center justify-center text-white font-bold flex-shrink-0`}>
                    {testimonial.initials}
                  </div>
                  <div className="flex-grow">
                    <div className="font-semibold text-gray-900 dark:text-white">
                      {testimonial.author}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {testimonial.role}, {testimonial.company}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};