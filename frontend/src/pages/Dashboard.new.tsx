import React, { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { TopNav } from '../components/TopNav';
import { Leads } from '../lib/api';
import toast from 'react-hot-toast';
import { Upload, Users, TrendingUp, Calendar } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Mock KPI data - in a real app, this would come from an API
  const kpis = [
    { name: 'Total Leads', value: '1,234', icon: Users, color: 'bg-blue-500' },
    { name: 'Last 7 Days', value: '87', icon: TrendingUp, color: 'bg-green-500' },
    { name: 'New Today', value: '12', icon: Calendar, color: 'bg-purple-500' },
  ];

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      toast.error('Please select a CSV file');
      return;
    }

    setUploading(true);
    try {
      const result = await Leads.bulkUpload(file);
      toast.success(`Successfully uploaded! Created: ${result.created}, Duplicates: ${result.duplicates}`);
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav />
      
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="px-4 py-6 sm:px-0">
          <div className="text-center">
            <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              24/7 AI Receptionist for Home Services
            </h1>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Never miss another lead. Our AI handles calls, qualifies prospects, and schedules appointments 
              automatically while you focus on growing your business.
            </p>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            {kpis.map((kpi) => (
              <div key={kpi.name} className="bg-white overflow-hidden shadow-sm rounded-xl">
                <div className="p-6">
                  <div className="flex items-center">
                    <div className={`flex-shrink-0 ${kpi.color} rounded-md p-3`}>
                      <kpi.icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          {kpi.name}
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {kpi.value}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow-sm rounded-xl">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {/* Upload CSV */}
                <div className="relative">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <button
                    onClick={triggerFileUpload}
                    disabled={uploading}
                    className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {uploading ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-2"></div>
                    ) : (
                      <Upload className="h-5 w-5 mr-2 text-gray-400" />
                    )}
                    {uploading ? 'Uploading...' : 'Upload CSV'}
                  </button>
                </div>

                {/* View Leads */}
                <Link
                  to="/leads"
                  className="w-full flex items-center justify-center px-4 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <Users className="h-5 w-5 mr-2" />
                  View Leads
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Features Highlight */}
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow-sm rounded-xl">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Why Choose LeadNest?</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="text-center">
                  <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                    <Calendar className="h-6 w-6" />
                  </div>
                  <h4 className="mt-4 text-lg font-medium text-gray-900">Auto-Scheduling</h4>
                  <p className="mt-2 text-sm text-gray-600">
                    AI books appointments directly in your calendar
                  </p>
                </div>
                <div className="text-center">
                  <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-md bg-green-500 text-white">
                    <Users className="h-6 w-6" />
                  </div>
                  <h4 className="mt-4 text-lg font-medium text-gray-900">Lead Qualification</h4>
                  <p className="mt-2 text-sm text-gray-600">
                    Smart filtering identifies your best prospects
                  </p>
                </div>
                <div className="text-center">
                  <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-md bg-purple-500 text-white">
                    <TrendingUp className="h-6 w-6" />
                  </div>
                  <h4 className="mt-4 text-lg font-medium text-gray-900">24/7 Availability</h4>
                  <p className="mt-2 text-sm text-gray-600">
                    Never miss a call, even after business hours
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
