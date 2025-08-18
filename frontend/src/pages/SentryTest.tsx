import React, { useState } from 'react';

const SentryTestPage: React.FC = () => {
  const [loading, setLoading] = useState(false);

  const triggerError = () => {
    // This will throw an error that Sentry should catch
    throw new Error("Test Sentry Integration - This is a deliberate error!");
  };

  const triggerUndefinedFunction = () => {
    // This will call an undefined function
    (window as any).myUndefinedFunction();
  };

  const triggerTypeError = () => {
    // This will cause a type error
    const obj: any = null;
    console.log(obj.someProperty.doesNotExist);
  };

  const triggerNetworkError = async () => {
    // This will cause a network error (should be filtered out by our beforeSend)
    try {
      await fetch('https://nonexistent-api.example.com/test');
    } catch (error) {
      throw new Error('Network Error: Failed to fetch data');
    }
  };

  const triggerManualSentry = async () => {
    // Manually capture exception with Sentry
    const Sentry = await import('@sentry/react');
    Sentry.captureException(new Error("Manual Sentry Test Error"));
    alert('Manual error sent to Sentry! Check your dashboard.');
  };

  const testPerformanceTrace = async () => {
    setLoading(true);
    const Sentry = await import('@sentry/react');
    
    try {
      // Use the performance API to measure timing
      const startTime = performance.now();
      
      // Add a breadcrumb for the performance test
      Sentry.addBreadcrumb({
        message: 'Started performance trace test',
        level: 'info',
        category: 'performance'
      });

      // Simulate some work
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Simulate API call timing
      const apiStart = performance.now();
      await new Promise(resolve => setTimeout(resolve, 500));
      const apiEnd = performance.now();
      
      const totalTime = performance.now() - startTime;
      
      // Manually capture performance data
      Sentry.addBreadcrumb({
        message: `Performance test completed in ${totalTime.toFixed(2)}ms`,
        level: 'info',
        category: 'performance',
        data: {
          totalTime: totalTime,
          apiTime: apiEnd - apiStart
        }
      });

      // Capture a custom message with performance data
      Sentry.captureMessage('Performance trace test completed', {
        level: 'info',
        tags: {
          test: 'performance',
          environment: process.env.NODE_ENV
        },
        extra: {
          totalTime,
          apiTime: apiEnd - apiStart,
          timestamp: new Date().toISOString()
        }
      });

      alert(`Performance test completed in ${totalTime.toFixed(2)}ms! Check Sentry dashboard.`);
    } catch (error) {
      Sentry.captureException(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const testBreadcrumbs = async () => {
    const Sentry = await import('@sentry/react');
    
    // Add custom breadcrumbs
    Sentry.addBreadcrumb({
      message: 'User clicked breadcrumb test button',
      level: 'info',
      category: 'user-interaction'
    });

    Sentry.addBreadcrumb({
      message: 'Simulating navigation',
      level: 'info',
      category: 'navigation',
      data: { from: '/sentry-test', to: '/dashboard' }
    });

    // Then trigger an error to see breadcrumbs
    throw new Error("Breadcrumb Test Error - Check breadcrumbs in Sentry!");
  };

  const getCurrentEnvironment = () => {
    return process.env.NODE_ENV || 'development';
  };

  const getCurrentRelease = () => {
    return process.env.REACT_APP_VERCEL_GIT_COMMIT_SHA || 
           process.env.VERCEL_GIT_COMMIT_SHA || 
           'local-dev';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              🐛 Sentry Error & Performance Testing
            </h1>
            <p className="text-gray-600 mb-4">
              Comprehensive testing for all Sentry features. Errors and performance traces should appear in your Sentry dashboard.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="text-sm text-blue-800">
                <strong>Current Environment:</strong> {getCurrentEnvironment()} | 
                <strong> Release:</strong> {getCurrentRelease().substring(0, 8)} |
                <strong> DSN Status:</strong> {process.env.REACT_APP_SENTRY_DSN ? '✅ Configured' : '❌ Missing'}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Basic Error Tests */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-red-800 mb-2">
                🔥 JavaScript Error
              </h3>
              <p className="text-red-600 text-sm mb-4">
                Throws a JavaScript Error that should be caught by Sentry
              </p>
              <button
                onClick={triggerError}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
              >
                Trigger Error
              </button>
            </div>

            <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-orange-800 mb-2">
                ⚠️ Undefined Function
              </h3>
              <p className="text-orange-600 text-sm mb-4">
                Calls myUndefinedFunction() which doesn't exist
              </p>
              <button
                onClick={triggerUndefinedFunction}
                className="bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 transition-colors"
              >
                Call Undefined Function
              </button>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">
                💥 Type Error
              </h3>
              <p className="text-yellow-600 text-sm mb-4">
                Tries to access property on null object
              </p>
              <button
                onClick={triggerTypeError}
                className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700 transition-colors"
              >
                Trigger Type Error
              </button>
            </div>

            {/* Advanced Tests */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-purple-800 mb-2">
                📊 Performance Trace
              </h3>
              <p className="text-purple-600 text-sm mb-4">
                Creates a performance trace with nested spans
              </p>
              <button
                onClick={testPerformanceTrace}
                disabled={loading}
                className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Testing...' : 'Test Performance'}
              </button>
            </div>

            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-indigo-800 mb-2">
                🍞 Breadcrumbs Test
              </h3>
              <p className="text-indigo-600 text-sm mb-4">
                Adds custom breadcrumbs then triggers error
              </p>
              <button
                onClick={testBreadcrumbs}
                className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 transition-colors"
              >
                Test Breadcrumbs
              </button>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-800 mb-2">
                🎯 Manual Capture
              </h3>
              <p className="text-green-600 text-sm mb-4">
                Manually sends an error to Sentry using captureException()
              </p>
              <button
                onClick={triggerManualSentry}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
              >
                Send Manual Error
              </button>
            </div>

            {/* Filtered Error Test */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 md:col-span-2 lg:col-span-1">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">
                🚫 Network Error (Filtered)
              </h3>
              <p className="text-blue-600 text-sm mb-4">
                Should be filtered out by beforeSend filter
              </p>
              <button
                onClick={triggerNetworkError}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
              >
                Trigger Network Error
              </button>
            </div>
          </div>

          <div className="mt-8 p-6 bg-gray-50 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-4">🔍 What to expect in Sentry Dashboard:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h5 className="font-medium text-gray-800 mb-2">Issues Tab:</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Error events with stack traces</li>
                  <li>• Environment tags (development, preview, production)</li>
                  <li>• Release information</li>
                  <li>• User context and breadcrumbs</li>
                  <li>• Browser and device information</li>
                </ul>
              </div>
              <div>
                <h5 className="font-medium text-gray-800 mb-2">Performance Tab:</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Custom transaction traces</li>
                  <li>• Page load performance</li>
                  <li>• API request timing</li>
                  <li>• Component render performance</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="mt-6 text-center">
            <a 
              href="/"
              className="text-blue-600 hover:text-blue-800 underline mr-4"
            >
              ← Back to Home
            </a>
            <a
              href="https://sentry.io"
              target="_blank"
              rel="noopener noreferrer"
              className="text-purple-600 hover:text-purple-800 underline"
            >
              Open Sentry Dashboard →
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SentryTestPage;
