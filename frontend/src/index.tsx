import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Enhanced Sentry configuration with release tracking and performance
if (process.env.REACT_APP_SENTRY_DSN) {
  import('@sentry/react').then(({ init }) => {
    // Determine environment and release
    const environment = process.env.REACT_APP_ENV_NAME || 
                       process.env.NODE_ENV || 
                       'development';
    
    const release = process.env.REACT_APP_VERCEL_GIT_COMMIT_SHA || 
                   process.env.VERCEL_GIT_COMMIT_SHA || 
                   `local-dev-${Date.now()}`;

    init({
      dsn: process.env.REACT_APP_SENTRY_DSN!,
      environment: environment,
      release: `leadnest-frontend@${release}`,
      
      // Performance Monitoring
      tracesSampleRate: environment === 'production' ? 0.1 : 1.0,
      
      // Enhanced error filtering
      beforeSend(event: any) {
        // Add custom tags to all events
        event.tags = {
          ...event.tags,
          deployment: environment,
          component: 'frontend',
          platform: 'react'
        };
        
        // Always allow test errors through
        if (event.exception) {
          const error = event.exception.values?.[0];
          if (error?.value?.includes('Test Sentry Integration') || 
              error?.value?.includes('Manual Sentry Test Error') ||
              error?.value?.includes('myUndefinedFunction')) {
            return event;
          }
          // Filter out expected errors
          if (error?.value?.includes('Network Error') || 
              error?.value?.includes('401') ||
              error?.value?.includes('403') ||
              error?.value?.includes('ChunkLoadError')) {
            return null;
          }
        }
        return event;
      },
      
      // Set initial user context
      initialScope: (scope: any) => {
        scope.setTag('component', 'frontend');
        scope.setTag('platform', 'react');
        scope.setTag('deployment', environment);
        scope.setUser({
          id: 'anonymous',
          environment: environment
        });
        return scope;
      }
    });
    
    console.log(`🐛 Sentry initialized successfully!`, {
      environment,
      release,
      dsn: process.env.REACT_APP_SENTRY_DSN?.substring(0, 50) + '...'
    });
  }).catch(err => {
    console.warn('Failed to load Sentry:', err);
  });
} else {
  console.warn('⚠️ REACT_APP_SENTRY_DSN not set - Sentry disabled');
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
