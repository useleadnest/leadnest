import React, { useState, useEffect } from 'react';
import { Search, Lead, DashboardStats } from '../types';
import { searchAPI, dashboardAPI, exportAPI } from '../services/api';
import { useAuth } from '../components/AuthContext';

const Dashboard: React.FC = () => {
  const [searches, setSearches] = useState<Search[]>([]);
  const [selectedSearch, setSelectedSearch] = useState<Search | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchForm, setSearchForm] = useState({ location: '', trade: '' });
  const { user, logout } = useAuth();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [searchData, statsData] = await Promise.all([
        searchAPI.getSearches(),
        dashboardAPI.getStats(),
      ]);
      setSearches(searchData);
      setStats(statsData);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const newSearch = await searchAPI.createSearch(searchForm);
      setSearches([newSearch, ...searches]);
      setSelectedSearch(newSearch);
      setSearchForm({ location: '', trade: '' });
      loadData(); // Refresh stats
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSearch = async (search: Search) => {
    setSelectedSearch(search);
    try {
      const searchLeads = await searchAPI.getSearchLeads(search.id);
      setLeads(searchLeads);
    } catch (error) {
      console.error('Error loading leads:', error);
    }
  };

  const handleExport = async (searchId: number) => {
    try {
      const blob = await exportAPI.downloadCSV(searchId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `leads_${searchId}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      // Create export record
      await exportAPI.createExport(searchId, 'csv');
      loadData(); // Refresh stats
    } catch (error) {
      alert('Export failed');
    }
  };

  const tradeOptions = [
    'Roofing', 'Solar', 'Pool', 'Painting', 'Plumbing', 
    'Electrical', 'HVAC', 'Landscaping', 'Construction', 'Remodeling'
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">LeadNest</h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user?.email}</span>
              {stats?.trial_days_left !== undefined && (
                <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm">
                  Trial: {stats.trial_days_left} days left
                </span>
              )}
              <button
                className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                onClick={async () => {
                  try {
                    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/seed-demo`, { method: 'POST' });
                    const json = await res.json();
                    alert(res.ok ? `Seeded: ${JSON.stringify(json)}` : `Failed: ${JSON.stringify(json)}`);
                  } catch (e) {
                    alert(String(e));
                  }
                }}
              >
                Seed Demo Data
              </button>
              <button
                onClick={logout}
                className="text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900">Searches</h3>
              <p className="text-3xl font-bold text-primary-600">{stats.total_searches}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900">Leads</h3>
              <p className="text-3xl font-bold text-primary-600">{stats.total_leads}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900">Exports</h3>
              <p className="text-3xl font-bold text-primary-600">{stats.total_exports}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900">Quality Score</h3>
              <p className="text-3xl font-bold text-primary-600">
                {leads.length > 0 
                  ? (leads.reduce((sum, lead) => sum + (lead.quality_score || 0), 0) / leads.length * 100).toFixed(0) + '%'
                  : 'N/A'
                }
              </p>
            </div>
          </div>
        )}

        {/* Search Form */}
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-bold mb-4">Generate New Leads</h2>
          <form onSubmit={handleSearch} className="flex gap-4">
            <input
              type="text"
              placeholder="Location (e.g., Austin, TX)"
              value={searchForm.location}
              onChange={(e) => setSearchForm({ ...searchForm, location: e.target.value })}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
            <select
              value={searchForm.trade}
              onChange={(e) => setSearchForm({ ...searchForm, trade: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            >
              <option value="">Select Trade</option>
              {tradeOptions.map(trade => (
                <option key={trade} value={trade.toLowerCase()}>{trade}</option>
              ))}
            </select>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
            >
              {loading ? 'Searching...' : 'Search Leads'}
            </button>
          </form>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Search History */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Search History</h2>
            <div className="space-y-3">
              {searches.map(search => (
                <div
                  key={search.id}
                  onClick={() => handleSelectSearch(search)}
                  className={`p-3 border rounded cursor-pointer hover:bg-gray-50 ${
                    selectedSearch?.id === search.id ? 'border-primary-500 bg-primary-50' : 'border-gray-200'
                  }`}
                >
                  <div className="font-medium">{search.trade} in {search.location}</div>
                  <div className="text-sm text-gray-600">
                    {search.results_count} leads • {new Date(search.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Leads Table */}
          <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">
                {selectedSearch ? `Leads: ${selectedSearch.trade} in ${selectedSearch.location}` : 'Select a search to view leads'}
              </h2>
              {selectedSearch && (
                <button
                  onClick={() => handleExport(selectedSearch.id)}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  Export CSV
                </button>
              )}
            </div>
            
            {leads.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full table-auto">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="px-4 py-2 text-left">Business</th>
                      <th className="px-4 py-2 text-left">Contact</th>
                      <th className="px-4 py-2 text-left">Rating</th>
                      <th className="px-4 py-2 text-left">Quality</th>
                      <th className="px-4 py-2 text-left">Messages</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leads.map(lead => (
                      <tr key={lead.id} className="border-t">
                        <td className="px-4 py-2">
                          <div className="font-medium">{lead.business_name}</div>
                          <div className="text-sm text-gray-600">{lead.category}</div>
                        </td>
                        <td className="px-4 py-2">
                          <div className="text-sm">
                            {lead.phone && <div>📞 {lead.phone}</div>}
                            {lead.email && <div>📧 {lead.email}</div>}
                            {lead.website && <div>🌐 <a href={lead.website} target="_blank" rel="noopener noreferrer" className="text-primary-600">Website</a></div>}
                          </div>
                        </td>
                        <td className="px-4 py-2">
                          {lead.rating && (
                            <div>
                              <div>⭐ {lead.rating}</div>
                              <div className="text-sm text-gray-600">({lead.review_count} reviews)</div>
                            </div>
                          )}
                        </td>
                        <td className="px-4 py-2">
                          {lead.quality_score && (
                            <div className={`px-2 py-1 rounded text-sm ${
                              lead.quality_score >= 0.7 ? 'bg-green-100 text-green-800' :
                              lead.quality_score >= 0.5 ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {Math.round(lead.quality_score * 100)}%
                            </div>
                          )}
                        </td>
                        <td className="px-4 py-2">
                          <div className="text-sm space-y-1">
                            {lead.ai_email_message && (
                              <div className="text-gray-600 truncate max-w-xs" title={lead.ai_email_message}>
                                📧 {lead.ai_email_message}
                              </div>
                            )}
                            {lead.ai_sms_message && (
                              <div className="text-gray-600 truncate max-w-xs" title={lead.ai_sms_message}>
                                📱 {lead.ai_sms_message}
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                {selectedSearch ? 'No leads found for this search.' : 'Select a search from the left to view leads.'}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
