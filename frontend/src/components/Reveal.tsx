'use client';

import React, { useEffect, useRef, useState } from 'react';

interface RevealProps {
  children: React.ReactNode;
  /** Stagger delay in ms once the element enters the viewport */
  delay?: number;
  className?: string;
  /** Vertical travel distance hint; default 16px */
  distance?: 'sm' | 'md' | 'lg';
}

const DISTANCES: Record<'sm' | 'md' | 'lg', string> = {
  sm: 'translate-y-2',
  md: 'translate-y-4',
  lg: 'translate-y-6',
};

/**
 * Restrained scroll reveal: fades and lifts children into place the first
 * time they enter the viewport. Respects prefers-reduced-motion by showing
 * content immediately and never running a transition.
 */
export default function Reveal({ children, delay = 0, className = '', distance = 'md' }: RevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    if (
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ) {
      setVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisible(true);
            observer.disconnect();
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -32px 0px' }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      style={{ transitionDelay: `${delay}ms` }}
      className={`transition-all duration-700 ease-out will-change-transform ${
        visible ? 'translate-y-0 opacity-100' : `opacity-0 ${DISTANCES[distance]}`
      } ${className}`}
    >
      {children}
    </div>
  );
}
