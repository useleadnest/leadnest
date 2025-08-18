import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { User, Billing } from '../lib/api';
import { AlertCircle, CreditCard, ExternalLink } from 'lucide-react';

interface SubscriptionGateProps {
  children: React.ReactNode;
}

export const SubscriptionGate: React.FC<SubscriptionGateProps> = ({ children }) => {
  const [userInfo, setUserInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserInfo();
  }, []);

  const loadUserInfo = async () => {
    try {
      const data = await User.me();
      setUserInfo(data);
    } catch (error) {
      console.error('Failed to load user info:', error);
      // If API doesn't exist yet, don't block the app
      setUserInfo({ subscription_status: 'active' });
    } finally {
      setLoading(false);
    }
  };

  const handleOpenPortal = async () => {
    try {
      const { url } = await Billing.createPortalSession();
      window.open(url, '_blank');
    } catch (error) {
      console.error('Failed to open portal:', error);
      // Fallback to billing page if portal doesn't work
      window.location.href = '/billing';
    }
  };

  if (loading) {
    return <>{children}</>;
  }

  const isInactive = userInfo?.subscription_status !== 'active';

  return (
    <>
      {isInactive && (
        <div className="bg-yellow-50 border-b border-yellow-200">
          <div className="max-w-7xl mx-auto py-3 px-3 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between flex-wrap">
              <div className="w-0 flex-1 flex items-center">
                <span className="flex p-2 rounded-lg bg-yellow-400">
                  <AlertCircle className="h-5 w-5 text-white" />
                </span>
                <p className="ml-3 font-medium text-yellow-800">
                  Your subscription is inactive. Please subscribe to continue using LeadNest.
                </p>
              </div>
              <div className="order-3 mt-2 flex-shrink-0 w-full sm:order-2 sm:mt-0 sm:w-auto">
                <div className="flex space-x-2">
                  <Link
                    to="/billing"
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-yellow-800 bg-yellow-200 hover:bg-yellow-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
                  >
                    <CreditCard className="h-4 w-4 mr-2" />
                    Upgrade Plan
                  </Link>
                  <button
                    onClick={handleOpenPortal}
                    className="inline-flex items-center px-4 py-2 border border-yellow-300 rounded-md shadow-sm text-sm font-medium text-yellow-800 bg-white hover:bg-yellow-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Billing Portal
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      {children}
    </>
  );
};
