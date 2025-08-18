import React, { useState, useEffect } from 'react';
import { TopNav } from '../components/TopNav';
import { User, Billing } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { ExternalLink, CreditCard, User as UserIcon } from 'lucide-react';

export const Settings: React.FC = () => {
  const [userInfo, setUserInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    loadUserInfo();
  }, []);

  const loadUserInfo = async () => {
    try {
      const data = await User.me();
      setUserInfo(data);
    } catch (error) {
      console.error('Failed to load user info:', error);
      // Don't show error toast as the endpoint might not be implemented yet
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCustomerPortal = async () => {
    try {
      const { url } = await Billing.createPortalSession();
      window.open(url, '_blank');
    } catch (error) {
      console.error('Failed to open customer portal:', error);
      toast.error('Customer portal is not available yet');
    }
  };

  const handleBookDemo = () => {
    const calendlyUrl = import.meta.env.VITE_CALENDLY_URL || 'https://calendly.com/leadnest-demo';
    window.open(calendlyUrl, '_blank');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav />
      
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            <p className="text-sm text-gray-600 mt-1">
              Manage your account and subscription settings
            </p>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Account Information */}
            <div className="lg:col-span-2 space-y-6">
              {/* Profile */}
              <div className="bg-white shadow-sm rounded-xl">
                <div className="px-6 py-4 border-b border-gray-200 flex items-center">
                  <UserIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <h3 className="text-lg font-medium text-gray-900">Profile</h3>
                </div>
                <div className="p-6">
                  {loading ? (
                    <div className="animate-pulse space-y-4">
                      <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Email Address
                        </label>
                        <p className="mt-1 text-sm text-gray-900">{user?.email}</p>
                      </div>
                      {userInfo?.plan && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700">
                            Current Plan
                          </label>
                          <p className="mt-1 text-sm text-gray-900 capitalize">
                            {userInfo.plan}
                          </p>
                        </div>
                      )}
                      {userInfo?.subscription_status && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700">
                            Subscription Status
                          </label>
                          <span className={`mt-1 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            userInfo.subscription_status === 'active' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {userInfo.subscription_status}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Subscription Management */}
              <div className="bg-white shadow-sm rounded-xl">
                <div className="px-6 py-4 border-b border-gray-200 flex items-center">
                  <CreditCard className="h-5 w-5 text-gray-400 mr-2" />
                  <h3 className="text-lg font-medium text-gray-900">Subscription</h3>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    <p className="text-sm text-gray-600">
                      Manage your billing information, view invoices, and update payment methods.
                    </p>
                    
                    <button
                      onClick={handleOpenCustomerPortal}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Open Customer Portal
                    </button>

                    <p className="text-xs text-gray-500">
                      The customer portal allows you to manage your subscription, download invoices, and update billing information.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="space-y-6">
              {/* Demo Booking */}
              <div className="bg-white shadow-sm rounded-xl">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Need Help?</h3>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    <p className="text-sm text-gray-600">
                      Book a demo with our team to learn more about LeadNest features and get personalized setup help.
                    </p>
                    
                    <button
                      onClick={handleBookDemo}
                      className="w-full inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Book a Demo
                    </button>
                  </div>
                </div>
              </div>

              {/* Account Status */}
              <div className="bg-white shadow-sm rounded-xl">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Account Status</h3>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    {userInfo?.subscription_status === 'active' ? (
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <div className="h-8 w-8 bg-green-500 rounded-full flex items-center justify-center">
                            <svg className="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium text-gray-900">Active Subscription</p>
                          <p className="text-sm text-gray-500">Your account is in good standing</p>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <div className="h-8 w-8 bg-yellow-500 rounded-full flex items-center justify-center">
                            <svg className="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                            </svg>
                          </div>
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium text-gray-900">Subscription Required</p>
                          <p className="text-sm text-gray-500">Please upgrade your plan to continue</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
