import React from 'react';
import { TopNav } from '../components/TopNav';
import { Billing as BillingAPI } from '../lib/api';
import toast from 'react-hot-toast';
import { Check, Star } from 'lucide-react';

export const Billing: React.FC = () => {
  const plans = [
    {
      name: 'Starter',
      price: '$299',
      period: '/month',
      description: 'Perfect for small businesses getting started',
      features: [
        'Up to 100 calls/month',
        'Basic AI receptionist',
        'Lead capture & qualification',
        'Email notifications',
        'Basic analytics',
      ],
      planId: 'starter' as const,
      popular: false,
    },
    {
      name: 'Pro',
      price: '$699',
      period: '/month',
      description: 'For growing businesses that need more',
      features: [
        'Up to 500 calls/month',
        'Advanced AI receptionist',
        'Smart appointment scheduling',
        'CRM integration',
        'Advanced analytics',
        'Priority support',
      ],
      planId: 'pro' as const,
      popular: true,
    },
    {
      name: 'Enterprise',
      price: '$1,299',
      period: '/month',
      description: 'For large businesses with high volume',
      features: [
        'Unlimited calls',
        'Custom AI training',
        'Multi-location support',
        'Custom integrations',
        'Dedicated account manager',
        'White-label options',
      ],
      planId: 'enterprise' as const,
      popular: false,
    },
  ];

  const handleSelectPlan = async (planId: 'starter' | 'pro' | 'enterprise') => {
    try {
      const { url } = await BillingAPI.createCheckoutSession(planId);
      window.location.href = url;
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      toast.error('Checkout is not available yet. Please contact support.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav />
      
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Choose Your Plan
            </h1>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Start your 14-day free trial. No credit card required.
            </p>
          </div>

          {/* Plans Grid */}
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`relative bg-white rounded-xl shadow-sm overflow-hidden ${
                  plan.popular ? 'ring-2 ring-blue-500' : 'border border-gray-200'
                }`}
              >
                {plan.popular && (
                  <div className="absolute top-0 right-0 -translate-y-px translate-x-px">
                    <div className="bg-blue-500 text-white px-3 py-1 text-sm font-medium rounded-bl-md flex items-center">
                      <Star className="h-4 w-4 mr-1 fill-current" />
                      Most Popular
                    </div>
                  </div>
                )}

                <div className="p-8">
                  {/* Plan Name */}
                  <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
                  <p className="mt-2 text-sm text-gray-600">{plan.description}</p>

                  {/* Price */}
                  <div className="mt-6">
                    <div className="flex items-baseline">
                      <span className="text-4xl font-extrabold text-gray-900">
                        {plan.price}
                      </span>
                      <span className="text-lg font-medium text-gray-500 ml-1">
                        {plan.period}
                      </span>
                    </div>
                  </div>

                  {/* Features */}
                  <ul className="mt-8 space-y-4">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start">
                        <div className="flex-shrink-0">
                          <Check className="h-5 w-5 text-green-500" />
                        </div>
                        <span className="ml-3 text-sm text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <div className="mt-8">
                    <button
                      onClick={() => handleSelectPlan(plan.planId)}
                      className={`w-full py-3 px-6 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                        plan.popular
                          ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
                          : 'bg-white text-blue-600 border border-blue-600 hover:bg-blue-50 focus:ring-blue-500'
                      }`}
                    >
                      Choose {plan.name}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* FAQ Section */}
          <div className="mt-16">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">Frequently Asked Questions</h2>
            </div>
            
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Can I change plans later?
                </h3>
                <p className="text-gray-600">
                  Yes, you can upgrade or downgrade your plan at any time. Changes take effect at your next billing cycle.
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  What's included in the free trial?
                </h3>
                <p className="text-gray-600">
                  You get full access to all Pro features for 14 days. No credit card required to start.
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Is there a setup fee?
                </h3>
                <p className="text-gray-600">
                  No setup fees! We'll help you get started with a personalized onboarding session included in all plans.
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Can I cancel anytime?
                </h3>
                <p className="text-gray-600">
                  Yes, you can cancel your subscription at any time with no cancellation fees. Your access continues until the end of your billing period.
                </p>
              </div>
            </div>
          </div>

          {/* Contact CTA */}
          <div className="mt-16 text-center">
            <div className="bg-blue-50 rounded-xl p-8">
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Need a custom solution?
              </h3>
              <p className="text-gray-600 mb-4">
                Get in touch for enterprise pricing and custom features.
              </p>
              <button
                onClick={() => {
                  const calendlyUrl = process.env.REACT_APP_CALENDLY_URL || 'https://calendly.com/leadnest-demo';
                  window.open(calendlyUrl, '_blank');
                }}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Schedule a Call
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
