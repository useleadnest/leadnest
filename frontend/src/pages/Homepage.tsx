import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { healthAPI } from '../lib/api';

const Homepage: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        await healthAPI.check();
        setApiStatus('online');
      } catch (error) {
        setApiStatus('offline');
      }
    };

    checkApiStatus();
    // Check API status every 30 seconds
    const interval = setInterval(checkApiStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleWatchDemo = () => {
    // Demo functionality would go here
    console.log('Demo clicked');
  };

  const scrollToFeatures = () => {
    const featuresSection = document.getElementById('features');
    if (featuresSection) {
      featuresSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="text-2xl font-bold text-blue-600">LeadNest</div>
            <div className="hidden md:flex space-x-8">
              <button 
                onClick={scrollToFeatures}
                className="text-gray-600 hover:text-gray-900 transition-colors font-medium"
              >
                Features
              </button>
              <Link 
                to="/login" 
                className="text-gray-600 hover:text-gray-900 transition-colors font-medium"
              >
                Sign In
              </Link>
              <Link 
                to="/signup" 
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-all duration-200 shadow-md hover:shadow-lg font-medium"
              >
                Get Started
              </Link>
            </div>
            {/* Mobile menu button */}
            <div className="md:hidden">
              <Link 
                to="/signup" 
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20">
        <div className="text-center">
          <div className="inline-flex items-center bg-blue-50 rounded-full px-4 py-2 text-blue-700 text-sm font-medium mb-8">
            🚀 Trusted by 10,000+ businesses worldwide
          </div>
          
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Generate Quality Leads
            <span className="text-blue-600 block">Effortlessly</span>
          </h1>
          
          <p className="text-lg sm:text-xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
            Transform your business with our AI-powered lead generation platform. 
            Identify, connect, and convert high-quality prospects with precision and speed.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link 
              to="/signup" 
              className="w-full sm:w-auto bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:bg-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              Start Your 7-Day Free Trial
            </Link>
            <button 
              onClick={handleWatchDemo}
              className="w-full sm:w-auto border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-xl text-lg font-semibold hover:border-blue-300 hover:text-blue-600 transition-all duration-200 bg-white hover:bg-blue-50"
            >
              Watch Demo
            </button>
          </div>

          <div className="mt-8 text-sm text-gray-500">
            No credit card required • Cancel anytime • 24/7 support
          </div>
        </div>

        {/* Features Grid */}
        <div id="features" className="mt-24 grid md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-2xl shadow-md hover:shadow-lg transition-all duration-300 border border-gray-100">
            <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center mb-6">
              <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-4">AI-Powered Discovery</h3>
            <p className="text-gray-600 leading-relaxed">
              Our advanced AI identifies high-quality prospects that match your ideal customer profile with 98% accuracy.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-md hover:shadow-lg transition-all duration-300 border border-gray-100">
            <div className="w-14 h-14 bg-green-100 rounded-xl flex items-center justify-center mb-6">
              <svg className="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-4">Verified Contact Data</h3>
            <p className="text-gray-600 leading-relaxed">
              Access accurate, up-to-date contact information with 95% deliverability guarantee and real-time verification.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-md hover:shadow-lg transition-all duration-300 border border-gray-100">
            <div className="w-14 h-14 bg-purple-100 rounded-xl flex items-center justify-center mb-6">
              <svg className="w-7 h-7 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-4">Smart Analytics</h3>
            <p className="text-gray-600 leading-relaxed">
              Track performance, measure ROI, and optimize your outreach with detailed insights and predictive analytics.
            </p>
          </div>
        </div>

        {/* Stats Section */}
        <div className="mt-24 bg-white rounded-2xl p-10 shadow-lg border border-gray-100">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Trusted by Industry Leaders</h2>
            <p className="text-gray-600">Join thousands of companies growing their business with LeadNest</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div className="space-y-2">
              <div className="text-4xl font-bold text-blue-600">10M+</div>
              <div className="text-gray-600 font-medium">Verified Contacts</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-blue-600">95%</div>
              <div className="text-gray-600 font-medium">Email Deliverability</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-blue-600">2.5x</div>
              <div className="text-gray-600 font-medium">Higher Conversion</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold text-blue-600">24/7</div>
              <div className="text-gray-600 font-medium">Customer Support</div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-24 text-center bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-12 text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Transform Your Lead Generation?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Start your free trial today and see how LeadNest can revolutionize your sales process.
          </p>
          <Link 
            to="/signup" 
            className="inline-block bg-white text-blue-600 px-8 py-4 rounded-xl text-lg font-semibold hover:bg-gray-50 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            Get Started Free
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="text-3xl font-bold mb-6">LeadNest</div>
            <p className="text-gray-400 mb-8 max-w-md mx-auto">
              The most powerful lead generation platform for growing businesses.
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 max-w-md mx-auto mb-8">
              <Link 
                to="/signup" 
                className="text-gray-400 hover:text-white transition-colors font-medium"
              >
                Get Started
              </Link>
              <Link 
                to="/login" 
                className="text-gray-400 hover:text-white transition-colors font-medium"
              >
                Sign In
              </Link>
              <button 
                onClick={scrollToFeatures}
                className="text-gray-400 hover:text-white transition-colors font-medium"
              >
                Features
              </button>
            </div>
            <div className="border-t border-gray-800 pt-8">
              <div className="flex justify-center items-center space-x-4 mb-4">
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    apiStatus === 'online' ? 'bg-green-500' : 
                    apiStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500'
                  }`}></div>
                  <span className="text-gray-500 text-sm">
                    API Status: {apiStatus === 'online' ? 'Online' : 
                                apiStatus === 'offline' ? 'Offline' : 'Checking...'}
                  </span>
                </div>
              </div>
              <p className="text-gray-500 text-sm">
                © 2025 LeadNest. All rights reserved.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Homepage;
