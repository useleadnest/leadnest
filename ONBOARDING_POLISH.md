# Onboarding Polish & Demo Mode

## Post-Payment Welcome Modal

### Implementation (src/components/WelcomeModal.tsx)
```tsx
import React, { useState, useEffect } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { CheckCircleIcon } from '@heroicons/react/24/outline';

interface WelcomeModalProps {
  isOpen: boolean;
  onClose: () => void;
  plan: string;
}

const WelcomeModal: React.FC<WelcomeModalProps> = ({ isOpen, onClose, plan }) => {
  const [currentStep, setCurrentStep] = useState(0);
  
  const steps = [
    {
      title: 'Welcome to LeadNest!',
      content: `Your ${plan} plan is now active. Let's get you set up for success.`,
      action: 'Get Started'
    },
    {
      title: 'Import Your First Leads',
      content: 'Upload a CSV file or connect your CRM to start building your lead database.',
      action: 'Import Leads'
    },
    {
      title: 'Set Up Notifications',
      content: 'Configure email alerts for new leads and important updates.',
      action: 'Configure Alerts'
    },
    {
      title: 'You\'re All Set!',
      content: 'Start generating leads and watch your business grow.',
      action: 'Go to Dashboard'
    }
  ];

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onClose();
    }
  };

  return (
    <Transition.Root show={isOpen} as={React.Fragment}>
      <Dialog as="div" className="relative z-10" onClose={onClose}>
        <Transition.Child
          as={React.Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={React.Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div>
                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
                    <CheckCircleIcon className="h-6 w-6 text-green-600" aria-hidden="true" />
                  </div>
                  <div className="mt-3 text-center sm:mt-5">
                    <Dialog.Title as="h3" className="text-base font-semibold leading-6 text-gray-900">
                      {steps[currentStep].title}
                    </Dialog.Title>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500">
                        {steps[currentStep].content}
                      </p>
                    </div>
                  </div>
                </div>
                
                {/* Progress indicator */}
                <div className="mt-5 flex justify-center space-x-2">
                  {steps.map((_, index) => (
                    <div
                      key={index}
                      className={`h-2 w-2 rounded-full ${
                        index <= currentStep ? 'bg-blue-600' : 'bg-gray-300'
                      }`}
                    />
                  ))}
                </div>
                
                <div className="mt-5 sm:mt-6">
                  <button
                    type="button"
                    className="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
                    onClick={nextStep}
                  >
                    {steps[currentStep].action}
                  </button>
                  {currentStep > 0 && (
                    <button
                      type="button"
                      className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                      onClick={() => setCurrentStep(currentStep - 1)}
                    >
                      Back
                    </button>
                  )}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
};

export default WelcomeModal;
```

## Empty States

### Leads Empty State (src/components/EmptyStates.tsx)
```tsx
import React from 'react';
import { PlusIcon, DocumentArrowUpIcon } from '@heroicons/react/24/outline';

export const LeadsEmptyState: React.FC<{ onImport: () => void; onAddLead: () => void }> = ({ 
  onImport, 
  onAddLead 
}) => (
  <div className="text-center py-12">
    <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
    <h3 className="mt-2 text-sm font-semibold text-gray-900">No leads yet</h3>
    <p className="mt-1 text-sm text-gray-500">
      Get started by importing leads from a CSV file or adding them manually.
    </p>
    <div className="mt-6 flex justify-center space-x-3">
      <button
        type="button"
        onClick={onImport}
        className="inline-flex items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500"
      >
        <DocumentArrowUpIcon className="-ml-0.5 mr-1.5 h-5 w-5" />
        Import CSV
      </button>
      <button
        type="button"
        onClick={onAddLead}
        className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
      >
        <PlusIcon className="-ml-0.5 mr-1.5 h-5 w-5" />
        Add Lead
      </button>
    </div>
  </div>
);

export const DashboardEmptyState: React.FC = () => (
  <div className="text-center py-12">
    <h3 className="mt-2 text-sm font-semibold text-gray-900">Welcome to LeadNest</h3>
    <p className="mt-1 text-sm text-gray-500">
      Your lead generation dashboard will come to life once you start importing leads.
    </p>
    <div className="mt-6">
      <button
        type="button"
        className="inline-flex items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500"
      >
        Get Started
      </button>
    </div>
  </div>
);
```

## Helpful Tooltips

### Tooltip Component (src/components/Tooltip.tsx)
```tsx
import React, { useState } from 'react';
import { InformationCircleIcon } from '@heroicons/react/20/solid';

interface TooltipProps {
  content: string;
  children?: React.ReactNode;
}

const Tooltip: React.FC<TooltipProps> = ({ content, children }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children || <InformationCircleIcon className="h-4 w-4 text-gray-400" />}
      </div>
      
      {isVisible && (
        <div className="absolute z-10 w-64 p-2 mt-2 text-sm text-white bg-gray-900 rounded-md shadow-lg -top-1 left-full ml-2">
          {content}
          <div className="absolute top-2 left-0 w-0 h-0 border-t-4 border-t-transparent border-b-4 border-b-transparent border-r-4 border-r-gray-900 -ml-1"></div>
        </div>
      )}
    </div>
  );
};

export default Tooltip;
```

## Demo/Sandbox Mode

### Demo Mode Provider (src/context/DemoContext.tsx)
```tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface DemoContextType {
  isDemoMode: boolean;
  setDemoMode: (enabled: boolean) => void;
  demoData: {
    leads: any[];
    stats: any;
  };
}

const DemoContext = createContext<DemoContextType | undefined>(undefined);

// Demo seed data
const DEMO_LEADS = [
  {
    id: 'demo-1',
    company_name: 'Acme Construction',
    contact_name: 'John Smith',
    email: 'john@acmeconstruction.com',
    phone: '555-0123',
    location: 'New York, NY',
    project_type: 'Commercial Renovation',
    budget: '$500K - $1M',
    timeline: '3-6 months',
    created_at: '2024-01-15T10:00:00Z'
  },
  {
    id: 'demo-2', 
    company_name: 'BuildRight LLC',
    contact_name: 'Sarah Johnson',
    email: 'sarah@buildright.com',
    phone: '555-0456',
    location: 'Los Angeles, CA',
    project_type: 'Residential Build',
    budget: '$250K - $500K',
    timeline: '6-12 months',
    created_at: '2024-01-14T14:30:00Z'
  },
  {
    id: 'demo-3',
    company_name: 'Metro Developers',
    contact_name: 'Mike Wilson',
    email: 'mike@metrodev.com', 
    phone: '555-0789',
    location: 'Chicago, IL',
    project_type: 'Mixed Use Development',
    budget: '$2M+',
    timeline: '12+ months',
    created_at: '2024-01-13T09:15:00Z'
  }
];

const DEMO_STATS = {
  totalLeads: 147,
  thisMonth: 23,
  conversionRate: 12.5,
  avgProjectValue: '$750K'
};

export const DemoProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isDemoMode, setDemoMode] = useState(false);

  const value = {
    isDemoMode,
    setDemoMode,
    demoData: {
      leads: DEMO_LEADS,
      stats: DEMO_STATS
    }
  };

  return <DemoContext.Provider value={value}>{children}</DemoContext.Provider>;
};

export const useDemo = () => {
  const context = useContext(DemoContext);
  if (context === undefined) {
    throw new Error('useDemo must be used within a DemoProvider');
  }
  return context;
};
```

### Demo Mode Toggle (Admin)
```tsx
// Add to admin settings or URL parameter
const toggleDemo = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const isDemoFromUrl = urlParams.get('demo') === 'true';
  
  if (isDemoFromUrl || process.env.REACT_APP_ENV_NAME === 'development') {
    setDemoMode(!isDemoMode);
  }
};
```

## Loading States

### Skeleton Components (src/components/Skeletons.tsx)
```tsx
import React from 'react';

export const TableSkeleton: React.FC = () => (
  <div className="animate-pulse">
    <div className="space-y-3">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="grid grid-cols-6 gap-4">
          <div className="h-4 bg-gray-300 rounded col-span-2"></div>
          <div className="h-4 bg-gray-300 rounded"></div>
          <div className="h-4 bg-gray-300 rounded"></div>
          <div className="h-4 bg-gray-300 rounded"></div>
          <div className="h-4 bg-gray-300 rounded"></div>
        </div>
      ))}
    </div>
  </div>
);

export const StatsSkeleton: React.FC = () => (
  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
    {[...Array(4)].map((_, i) => (
      <div key={i} className="bg-white overflow-hidden shadow rounded-lg animate-pulse">
        <div className="p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-gray-300 rounded"></div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <div className="h-4 bg-gray-300 rounded mb-2"></div>
              <div className="h-6 bg-gray-300 rounded w-20"></div>
            </div>
          </div>
        </div>
      </div>
    ))}
  </div>
);
```

## Progressive Disclosure

### Expandable Sections
```tsx
import React, { useState } from 'react';
import { ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/20/solid';

const ExpandableSection: React.FC<{
  title: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
}> = ({ title, children, defaultExpanded = false }) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className="border rounded-lg">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-gray-50"
      >
        <span className="font-medium text-gray-900">{title}</span>
        {isExpanded ? (
          <ChevronDownIcon className="h-5 w-5 text-gray-500" />
        ) : (
          <ChevronRightIcon className="h-5 w-5 text-gray-500" />
        )}
      </button>
      
      {isExpanded && (
        <div className="px-4 pb-3 border-t border-gray-200">
          {children}
        </div>
      )}
    </div>
  );
};
```

## Success/Error Feedback

### Toast Notifications (src/components/Toast.tsx)
```tsx
import React, { useEffect } from 'react';
import { CheckCircleIcon, XCircleIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface ToastProps {
  type: 'success' | 'error';
  message: string;
  isVisible: boolean;
  onClose: () => void;
  autoClose?: boolean;
  duration?: number;
}

const Toast: React.FC<ToastProps> = ({ 
  type, 
  message, 
  isVisible, 
  onClose, 
  autoClose = true, 
  duration = 5000 
}) => {
  useEffect(() => {
    if (autoClose && isVisible) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [autoClose, isVisible, duration, onClose]);

  if (!isVisible) return null;

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm w-full">
      <div className={`rounded-md p-4 shadow-lg ${
        type === 'success' ? 'bg-green-50' : 'bg-red-50'
      }`}>
        <div className="flex">
          <div className="flex-shrink-0">
            {type === 'success' ? (
              <CheckCircleIcon className="h-5 w-5 text-green-400" />
            ) : (
              <XCircleIcon className="h-5 w-5 text-red-400" />
            )}
          </div>
          <div className="ml-3">
            <p className={`text-sm font-medium ${
              type === 'success' ? 'text-green-800' : 'text-red-800'
            }`}>
              {message}
            </p>
          </div>
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                onClick={onClose}
                className={`inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                  type === 'success' 
                    ? 'text-green-500 hover:bg-green-100 focus:ring-green-600'
                    : 'text-red-500 hover:bg-red-100 focus:ring-red-600'
                }`}
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Toast;
```
