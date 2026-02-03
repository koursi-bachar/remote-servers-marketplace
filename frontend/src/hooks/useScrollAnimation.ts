import { useAnimation } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { useEffect } from 'react';

export const useScrollAnimation = (threshold = 0.05, delay = 0, fadeOut = false) => { // Added fadeOut param
  const controls = useAnimation();
  const [ref, inView] = useInView({
    threshold: threshold, // Lower = triggers earlier
    triggerOnce: false,
    rootMargin: '-150px 0px' // Increased from -50px to -150px for earlier trigger
  });

  useEffect(() => {
    if (inView) {
      controls.start({
        opacity: 1,
        y: 0,
        transition: {
          duration: 0.8, // Increased from 0.5 to 0.8 for longer fade
          delay: delay,
          ease: "easeOut"
        }
      });
    } else if (fadeOut) {
      // Only fade out if explicitly enabled
      controls.start({
        opacity: 0,
        y: 20,
        transition: {
          duration: 0.5,
          ease: "easeIn"
        }
      });
    }
    // If fadeOut is false and not in view, do nothing (stays visible)
  }, [controls, inView, delay, fadeOut]);

  return { ref, controls };
};