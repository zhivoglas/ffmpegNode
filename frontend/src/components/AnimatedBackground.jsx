import React, { useState, useEffect } from 'react';
/* eslint-disable no-unused-vars */
import { motion, AnimatePresence } from 'framer-motion'; 

const defaultImages = [
  'https://dl.dropboxusercontent.com/scl/fi/ejutwzhg2cp9fxs5upew0/blue-309761.svg?rlkey=6yf2o9n3aki2offtp54rkfaoe&raw=1',
  'https://dl.dropboxusercontent.com/scl/fi/0abaznu4zzf23k869yehx/ai-generated-8959902.svg?rlkey=xnhu76el8aej76ef5mmfg4mlt&raw=1',
  'https://dl.dropboxusercontent.com/scl/fi/1jg5r27v3o9z0278k99nx/airplane-5040376.svg?rlkey=yi0m4uwk6pm35ep2dxqco83db&raw=1'
];

export default function AnimatedBackground({ images = defaultImages, settings }) {
  const safeSettings = settings || {
    opacity: 0.4,
    transitionDuration: 2,
    holdDuration: 5,
    scale: 1.1,
    transitionType: 'zoom',
    enableAnimation: true,
    selectedImage: 'auto'
  };

  const { opacity, transitionDuration, holdDuration, scale, transitionType, enableAnimation, selectedImage } = safeSettings;
  const [timerIndex, setTimerIndex] = useState(0);
  const [randomAnimType, setRandomAnimType] = useState('fade');
  const currentIndex = selectedImage !== 'auto' 
    ? parseInt(selectedImage, 10) 
    : timerIndex;

  useEffect(() => {
    if (selectedImage !== 'auto' || !enableAnimation) {
      return;
    }

    const timer = setInterval(() => {
      setTimerIndex((prev) => (prev + 1) % images.length);
      
      if (transitionType === 'random') {
        const types = ['fade', 'zoom', 'slide-left', 'slide-right', 'slide-up', 'slide-down'];
        setRandomAnimType(types[Math.floor(Math.random() * types.length)]);
      }
    }, holdDuration * 1000);

    return () => clearInterval(timer);
  }, [images.length, holdDuration, transitionType, enableAnimation, selectedImage]);

  const activeType = transitionType === 'random' ? randomAnimType : transitionType;
  const animations = {
    none: {
      initial: { opacity: 0 },
      animate: { opacity: opacity },
      exit: { opacity: 0 }
    },
    fade: {
      initial: { opacity: 0, scale: 1, x: 0, y: 0 },
      animate: { opacity: opacity, scale: 1, x: 0, y: 0 },
      exit: { opacity: 0, scale: 1, x: 0, y: 0 }
    },
    zoom: {
      initial: { opacity: 0, scale: scale, x: 0, y: 0 },
      animate: { opacity: opacity, scale: 1, x: 0, y: 0 },
      exit: { opacity: 0, scale: scale, x: 0, y: 0 }
    },
    'slide-left': {
      initial: { opacity: 0, scale: 1, x: 100, y: 0 },
      animate: { opacity: opacity, scale: 1, x: 0, y: 0 },
      exit: { opacity: 0, scale: 1, x: -100, y: 0 }
    },
    'slide-right': {
      initial: { opacity: 0, scale: 1, x: -100, y: 0 },
      animate: { opacity: opacity, scale: 1, x: 0, y: 0 },
      exit: { opacity: 0, scale: 1, x: 100, y: 0 }
    },
    'slide-up': {
      initial: { opacity: 0, scale: 1, x: 0, y: 100 },
      animate: { opacity: opacity, scale: 1, x: 0, y: 0 },
      exit: { opacity: 0, scale: 1, x: 0, y: -100 }
    },
    'slide-down': {
      initial: { opacity: 0, scale: 1, x: 0, y: -100 },
      animate: { opacity: opacity, scale: 1, x: 0, y: 0 },
      exit: { opacity: 0, scale: 1, x: 0, y: 100 }
    }
  };

  const activeAnim = animations[activeType] || animations.fade;
  const actualDuration = (enableAnimation && selectedImage === 'auto' && activeType !== 'none') ? transitionDuration : 0;

  return (
    <div style={{
      position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
      overflow: 'hidden', pointerEvents: 'none', zIndex: 0, backgroundColor: '#0f172a' 
    }}>
      <AnimatePresence mode="popLayout">
        <motion.img
          key={currentIndex}
          src={images[currentIndex]}
          alt="Animated Background"
          initial={activeAnim.initial}
          animate={activeAnim.animate}
          exit={activeAnim.exit}
          transition={{ duration: actualDuration, ease: "easeInOut" }}
          style={{
            position: 'absolute', inset: 0, width: '100%', height: '100%',
            objectFit: 'cover', objectPosition: 'center',
            willChange: 'opacity, transform'
          }}
        />
      </AnimatePresence>
    </div>
  );
}
