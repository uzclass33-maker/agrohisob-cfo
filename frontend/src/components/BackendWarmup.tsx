'use client';

import { useEffect } from 'react';
import { getApiBaseUrl } from '@/lib/api';

export default function BackendWarmup() {
  useEffect(() => {
    // Silently pre-warm the Render backend as soon as a user visits any page
    const warmUp = async () => {
      try {
        const baseUrl = getApiBaseUrl();
        await fetch(`${baseUrl}/health`, {
          method: 'GET',
          cache: 'no-store',
          keepalive: true,
        });
      } catch {
        // Silent catch: pre-warming failure should never degrade UI
      }
    };

    warmUp();

    // Heartbeat every 8 minutes while the browser tab remains open
    const interval = setInterval(warmUp, 8 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return null;
}
