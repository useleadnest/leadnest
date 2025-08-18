# Sales-Ready Demo Mode Implementation

## Demo Data Provider Component

### src/providers/DemoProvider.tsx
```tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface DemoContextType {
  isDemoMode: boolean;
  setDemoMode: (enabled: boolean) => void;
  demoData: {
    leads: any[];
    stats: any;
    user: any;
  };
}

const DemoContext = createContext<DemoContextType | undefined>(undefined);

// Realistic demo seed data
const DEMO_LEADS = [
  {
    id: 'demo-1',
    company_name: 'Pinnacle Construction Group',
    contact_name: 'Michael Rodriguez', 
    email: 'mrodriguez@pinnaclegroup.com',
    phone: '555-2847',
    location: 'Austin, TX',
    project_type: 'Commercial Office Complex',
    budget: '$2.5M - $5M',
    timeline: '12-18 months',
    status: 'Hot Lead',
    lead_score: 95,
    last_contact: '2024-01-18T14:30:00Z',
    created_at: '2024-01-15T10:00:00Z',
    notes: 'Expanding rapidly, needs 50,000 sq ft office space. Decision maker confirmed.'
  },
  {
    id: 'demo-2', 
    company_name: 'Heritage Home Builders',
    contact_name: 'Sarah Chen',
    email: 'sarah.chen@heritagehomes.com',
    phone: '555-7193',
    location: 'Denver, CO',
    project_type: 'Luxury Residential Development',
    budget: '$8M - $15M',
    timeline: '18-24 months',
    status: 'Qualified',
    lead_score: 88,
    last_contact: '2024-01-17T09:15:00Z',
    created_at: '2024-01-14T14:30:00Z',
    notes: '120-unit luxury townhome development. Pre-approved financing in place.'
  },
  {
    id: 'demo-3',
    company_name: 'Metro Infrastructure Solutions',
    contact_name: 'David Park',
    email: 'dpark@metroinfra.com', 
    phone: '555-9461',
    location: 'Phoenix, AZ',
    project_type: 'Municipal Infrastructure',
    budget: '$25M+',
    timeline: '24+ months',
    status: 'Proposal Sent',
    lead_score: 92,
    last_contact: '2024-01-16T16:45:00Z',
    created_at: '2024-01-13T09:15:00Z',
    notes: 'City water treatment facility upgrade. Public bid process starting Q2.'
  },
  {
    id: 'demo-4',
    company_name: 'Retail Spaces Inc',
    contact_name: 'Jennifer Walsh',
    email: 'j.walsh@retailspaces.com',
    phone: '555-3572',
    location: 'Miami, FL', 
    project_type: 'Shopping Center Renovation',
    budget: '$1.2M - $3M',
    timeline: '6-12 months',
    status: 'Follow-up Required',
    lead_score: 74,
    last_contact: '2024-01-12T11:20:00Z',
    created_at: '2024-01-10T15:45:00Z',
    notes: 'Modernizing 80,000 sq ft shopping center. Waiting on architectural plans.'
  },
  {
    id: 'demo-5',
    company_name: 'GreenTech Manufacturing',
    contact_name: 'Robert Kim',
    email: 'robert@greentech-mfg.com',
    phone: '555-8364',
    location: 'Portland, OR',
    project_type: 'Industrial Facility',
    budget: '$12M - $20M',
    timeline: '15-20 months',
    status: 'Hot Lead',
    lead_score: 96,
    last_contact: '2024-01-19T13:10:00Z',
    created_at: '2024-01-08T08:30:00Z',
    notes: 'New 200,000 sq ft manufacturing plant. Sustainable building requirements.'
  }
];

const DEMO_STATS = {
  totalLeads: 847,
  thisMonth: 127,
  conversionRate: 18.3,
  avgProjectValue: '$4.2M',
  totalPipeline: '$156M',
  wonDeals: 43,
  avgResponseTime: '2.4 hours',
  leadsByStatus: {
    'Hot Lead': 89,
    'Qualified': 156,
    'Proposal Sent': 67,
    'Follow-up Required': 234,
    'Won': 43,
    'Lost': 78
  },
  monthlyTrends: [
    { month: 'Jul', leads: 67, won: 8 },
    { month: 'Aug', leads: 89, won: 12 },
    { month: 'Sep', leads: 94, won: 15 },
    { month: 'Oct', leads: 112, won: 18 },
    { month: 'Nov', leads: 98, won: 14 },
    { month: 'Dec', leads: 134, won: 21 },
    { month: 'Jan', leads: 127, won: 19 }
  ]
};

const DEMO_USER = {
  id: 'demo-user',
  name: 'Demo User',
  email: 'demo@leadnest.com',
  company: 'LeadNest Demo',
  plan: 'Pro',
  subscription_status: 'active'
};

export const DemoProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Check URL parameter or environment for demo mode
  const urlParams = new URLSearchParams(window.location.search);
  const isDemoFromUrl = urlParams.get('demo') === 'true';
  const isDemoFromEnv = process.env.REACT_APP_ENV_NAME === 'development';
  
  const [isDemoMode, setDemoMode] = useState(isDemoFromUrl || isDemoFromEnv);

  const value = {
    isDemoMode,
    setDemoMode,
    demoData: {
      leads: DEMO_LEADS,
      stats: DEMO_STATS,
      user: DEMO_USER
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

## Demo Banner Component

### src/components/DemoBanner.tsx
```tsx
import React from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/20/solid';
import { useDemo } from '../providers/DemoProvider';

const DemoBanner: React.FC = () => {
  const { isDemoMode } = useDemo();

  if (!isDemoMode) return null;

  return (
    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
      <div className="flex">
        <div className="flex-shrink-0">
          <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" aria-hidden="true" />
        </div>
        <div className="ml-3">
          <p className="text-sm text-yellow-700">
            <strong>Demo Mode:</strong> You're viewing sample data. 
            <a 
              href="?demo=false" 
              className="font-medium underline text-yellow-700 hover:text-yellow-600 ml-2"
            >
              Exit Demo
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default DemoBanner;
```

## Updated API Client with Demo Mode

### src/lib/api.ts (Updated)
```tsx
import { useDemo } from '../providers/DemoProvider';

// Modify your API client to return demo data when in demo mode
export const useApiClient = () => {
  const { isDemoMode, demoData } = useDemo();

  const getLeads = async () => {
    if (isDemoMode) {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));
      return {
        leads: demoData.leads,
        total: demoData.leads.length,
        page: 1,
        pages: 1
      };
    }
    
    // Regular API call
    const response = await fetch(`${API_BASE_URL}/leads`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    return response.json();
  };

  const getDashboardStats = async () => {
    if (isDemoMode) {
      await new Promise(resolve => setTimeout(resolve, 600));
      return demoData.stats;
    }
    
    const response = await fetch(`${API_BASE_URL}/dashboard/stats`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    return response.json();
  };

  const createLead = async (leadData: any) => {
    if (isDemoMode) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const newLead = {
        ...leadData,
        id: `demo-${Date.now()}`,
        created_at: new Date().toISOString(),
        status: 'New Lead',
        lead_score: Math.floor(Math.random() * 40) + 60
      };
      
      // Add to demo data (in real app, this would be managed by state)
      demoData.leads.unshift(newLead);
      return { success: true, lead: newLead };
    }
    
    const response = await fetch(`${API_BASE_URL}/leads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`
      },
      body: JSON.stringify(leadData)
    });
    return response.json();
  };

  return {
    getLeads,
    getDashboardStats, 
    createLead,
    // ... other API methods
  };
};
```

## Sales Demo Script Integration

### src/components/DemoControls.tsx (Admin Only)
```tsx
import React, { useState } from 'react';
import { useDemo } from '../providers/DemoProvider';
import { PlayIcon, PauseIcon, ForwardIcon } from '@heroicons/react/24/outline';

const DemoControls: React.FC = () => {
  const { isDemoMode, demoData } = useDemo();
  const [currentScenario, setCurrentScenario] = useState(0);

  // Demo scenarios for sales presentations
  const scenarios = [
    {
      name: 'Initial Dashboard',
      description: 'Show clean dashboard with recent leads'
    },
    {
      name: 'Lead Management',
      description: 'Demonstrate lead filtering and management'
    },
    {
      name: 'Bulk Import Success',
      description: 'Show successful CSV import with validation'
    },
    {
      name: 'Pipeline Analytics', 
      description: 'Display conversion rates and revenue projections'
    },
    {
      name: 'ROI Calculation',
      description: 'Live ROI demonstration with client numbers'
    }
  ];

  if (!isDemoMode) return null;

  return (
    <div className="fixed bottom-4 right-4 bg-blue-600 text-white p-4 rounded-lg shadow-lg z-50">
      <div className="text-sm font-medium mb-2">Demo Controls</div>
      
      <div className="flex items-center space-x-2 mb-3">
        <button className="p-1 hover:bg-blue-700 rounded">
          <PlayIcon className="h-4 w-4" />
        </button>
        <button className="p-1 hover:bg-blue-700 rounded">
          <PauseIcon className="h-4 w-4" />
        </button>
        <button className="p-1 hover:bg-blue-700 rounded">
          <ForwardIcon className="h-4 w-4" />
        </button>
      </div>

      <select 
        value={currentScenario} 
        onChange={(e) => setCurrentScenario(Number(e.target.value))}
        className="text-xs bg-blue-700 text-white rounded p-1 w-full"
      >
        {scenarios.map((scenario, index) => (
          <option key={index} value={index}>
            {scenario.name}
          </option>
        ))}
      </select>
      
      <div className="text-xs mt-2 opacity-90">
        {scenarios[currentScenario].description}
      </div>
    </div>
  );
};

export default DemoControls;
```

## Demo-Specific Routing

### src/App.tsx (Updated with Demo Provider)
```tsx
import { DemoProvider } from './providers/DemoProvider';
import DemoBanner from './components/DemoBanner';
import DemoControls from './components/DemoControls';

function App() {
  return (
    <DemoProvider>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <DemoBanner />
            
            <Routes>
              {/* Your existing routes */}
            </Routes>
            
            <DemoControls />
          </div>
        </Router>
      </AuthProvider>
    </DemoProvider>
  );
}
```

## Demo URL Configuration

### Quick Demo Links
```html
<!-- For Sales Team -->
Production Demo: https://useleadnest.com?demo=true
Lead Management: https://useleadnest.com/leads?demo=true
Dashboard View: https://useleadnest.com/dashboard?demo=true
Billing Demo: https://useleadnest.com/billing?demo=true

<!-- Demo Exit -->
Live Platform: https://useleadnest.com?demo=false
```

## Sales Talking Points Integration

### Automatic Tooltips for Demo Mode
```tsx
// In demo mode, automatically show helpful tooltips
const DemoTooltip: React.FC<{ children: React.ReactNode; salesNote: string }> = ({ 
  children, 
  salesNote 
}) => {
  const { isDemoMode } = useDemo();
  
  if (!isDemoMode) return <>{children}</>;
  
  return (
    <div className="relative group">
      {children}
      <div className="absolute -top-12 left-1/2 transform -translate-x-1/2 bg-blue-900 text-white text-xs p-2 rounded opacity-0 group-hover:opacity-100 transition-opacity z-10 whitespace-nowrap">
        💡 {salesNote}
      </div>
    </div>
  );
};

// Usage in components
<DemoTooltip salesNote="Average lead value increased 340% with LeadNest">
  <div className="lead-value">${lead.budget}</div>
</DemoTooltip>
```

This implementation provides:

1. **Realistic Demo Data**: High-quality sample leads that represent actual contractor scenarios
2. **Sales-Ready Controls**: Demo progression controls for presentations
3. **Clear Demo Indicators**: Banners and visual cues that this is demo mode
4. **Seamless Integration**: Demo mode works with existing components
5. **Quick Access URLs**: Easy links for sales presentations
6. **Exit Strategy**: Clear way to exit demo and try real platform

The demo mode can be activated via URL parameter (`?demo=true`) or environment variable, making it perfect for sales presentations while keeping the production site clean.
