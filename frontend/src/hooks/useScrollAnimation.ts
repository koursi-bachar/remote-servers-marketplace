import { useAnimation } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { useEffect } from 'react';

export const useScrollAnimation = (threshold = 0.05, delay = 0, fadeOut = false) => {
  const controls = useAnimation();
  const [ref, inView] = useInView({
    threshold: threshold,
    triggerOnce: false,
    rootMargin: '-150px 0px'
  });

  useEffect(() => {
    if (inView) {
      controls.start({
        opacity: 1,
        y: 0,
        transition: {
          duration: 0.8,
          delay: delay,
          ease: "easeOut"
        }
      });
    } else if (fadeOut) {
      controls.start({
        opacity: 0,
        y: 20,
        transition: {
          duration: 0.5,
          ease: "easeIn"
        }
      });
    }
  }, [controls, inView, delay, fadeOut]);

  return { ref, controls };
};