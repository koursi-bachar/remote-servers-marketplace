import { useAnimation } from 'framer-motion';
import { useEffect } from 'react';

export const useFadeIn = (delay = 0) => {
  const controls = useAnimation();

  useEffect(() => {
    const timer = setTimeout(() => {
      controls.start({
        opacity: 1,
        y: 0,
        transition: { duration: 0.5, ease: 'easeOut' }
      });
    }, delay);

    return () => clearTimeout(timer);
  }, [controls, delay]);

  return controls;
};