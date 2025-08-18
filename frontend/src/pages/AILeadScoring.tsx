import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  CloudArrowUpIcon, 
  ChartBarIcon, 
  StarIcon, 
  DocumentChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';

interface Lead {
  id: string;
  name: string;
  email: string;
  phone: string;
  source: string;
  industry: string;
  score?: number;
  grade?: string;
}

interface ScoredLead {
  lead_id: string;
  score: number;
  grade: string;
  confidence: number;
  factors: string[];
}

interface ScoreStats {
  total_leads: number;
  avg_score: number;
  grade_distribution: { [key: string]: number };
  high_value_count: number;
}

const AILeadScoring: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [scoredLeads, setScoredLeads] = useState<ScoredLead[]>([]);
  const [stats, setStats] = useState<ScoreStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [viewMode, setViewMode] = useState<'table' | 'analytics'>('table');
  const [filters, setFilters] = useState({
    minScore: 0,
    grade: 'all',
    source: 'all'
  });
  
  // Load existing scored leads on component mount
  useEffect(() => {
    loadScoredLeads();
  }, []);

  const loadScoredLeads = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/ai/scored-leads', {
        params: {
          page: 1,
          per_page: 50,
          min_score: filters.minScore,
          grade: filters.grade !== 'all' ? filters.grade : undefined,
          source: filters.source !== 'all' ? filters.source : undefined
        }
      });
      
      setScoredLeads(response.data.leads || []);
      setStats(response.data.stats);
    } catch (err: any) {
      console.error('Failed to load scored leads:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        setCsvFile(file);
        setError(null);
        setSuccess(null);
      } else {
        setError('Please select a valid CSV file');
        setCsvFile(null);
      }
    }
  };

  const handleBulkScoring = async () => {
    if (!csvFile) {
      setError('Please select a CSV file first');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Parse CSV and convert to leads array (simplified for demo)
      const text = await csvFile.text();
      const rows = text.split('\n').filter(row => row.trim());
      const headers = rows[0].split(',').map(h => h.trim().toLowerCase());
      
      const parsedLeads = rows.slice(1).map((row, index) => {
        const values = row.split(',').map(v => v.trim());
        return {
          id: `csv_${index}`,
          name: values[headers.indexOf('name')] || values[0] || `Lead ${index + 1}`,
          email: values[headers.indexOf('email')] || values[1] || `lead${index + 1}@example.com`,
          phone: values[headers.indexOf('phone')] || values[2] || '+1234567890',
          source: values[headers.indexOf('source')] || 'csv_upload',
          industry: values[headers.indexOf('industry')] || 'general'
        };
      });
      
      setLeads(parsedLeads);

      // Score the leads
      const scoreResponse = await axios.post('/api/ai/bulk-score-leads', {
        leads: parsedLeads
      });

      setScoredLeads(scoreResponse.data.scored_leads || []);
      setStats(scoreResponse.data.stats);
      setSuccess(`Successfully scored ${parsedLeads.length} leads!`);
      
      // Clear file input
      setCsvFile(null);
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to score leads');
    } finally {
      setLoading(false);
    }
  };

  const exportResults = async () => {
    try {
      const response = await axios.get('/api/ai/export-scores', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `lead_scores_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to export results');
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getGradeBadgeColor = (grade: string): string => {
    switch (grade) {
      case 'A+':
      case 'A': return 'bg-green-100 text-green-800';
      case 'B': return 'bg-yellow-100 text-yellow-800';
      case 'C': return 'bg-orange-100 text-orange-800';
      default: return 'bg-red-100 text-red-800';
    }
  };

  const filteredLeads = scoredLeads.filter(lead => {
    if (lead.score < filters.minScore) return false;
    if (filters.grade !== 'all' && lead.grade !== filters.grade) return false;
    const leadData = leads.find(l => l.id === lead.lead_id);
    if (filters.source !== 'all' && leadData?.source !== filters.source) return false;
    return true;
  });

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <StarIcon className="w-8 h-8 text-yellow-500 mr-3" />
          AI Lead Scoring
        </h1>
        <p className="text-gray-600 mt-2">
          Upload leads and get AI-powered quality scores to prioritize your sales efforts
        </p>
      </div>
      
      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <CloudArrowUpIcon className="w-6 h-6 text-blue-500 mr-2" />
          Upload Leads for Scoring
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              CSV File Upload
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
              <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="mt-2 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              <p className="text-sm text-gray-500 mt-2">
                Upload a CSV with columns: name, email, phone, source, industry
              </p>
            </div>
          </div>

          <div className="flex flex-col justify-center">
            {csvFile && (
              <div className="bg-blue-50 rounded-lg p-4 mb-4">
                <div className="flex items-center">
                  <DocumentChartBarIcon className="w-6 h-6 text-blue-500 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-blue-900">
                      {csvFile.name}
                    </p>
                    <p className="text-sm text-blue-700">
                      {(csvFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
              </div>
            )}

            <button
              onClick={handleBulkScoring}
              disabled={!csvFile || loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Scoring Leads...
                </>
              ) : (
                <>
                  <ChartBarIcon className="w-5 h-5 mr-2" />
                  Score Leads
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Success/Error Messages */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 flex items-center">
          <ExclamationTriangleIcon className="w-6 h-6 mr-2" />
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6 flex items-center">
          <CheckCircleIcon className="w-6 h-6 mr-2" />
          {success}
        </div>
      )}

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <DocumentChartBarIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Leads</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.total_leads}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <ChartBarIcon className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Avg Score</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.avg_score.toFixed(1)}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <StarIcon className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">High Value</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.high_value_count}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <DocumentChartBarIcon className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">A+ Grades</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.grade_distribution['A+'] || 0}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* View Toggle and Filters */}
      {scoredLeads.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex flex-wrap items-center justify-between gap-4">
            {/* View Toggle */}
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('table')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  viewMode === 'table' 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-500'
                }`}
              >
                Table View
              </button>
              <button
                onClick={() => setViewMode('analytics')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  viewMode === 'analytics' 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-500'
                }`}
              >
                Analytics View
              </button>
            </div>

            {/* Filters */}
            <div className="flex gap-4 flex-wrap">
              <select
                value={filters.grade}
                onChange={(e) => setFilters(prev => ({ ...prev, grade: e.target.value }))}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm"
              >
                <option value="all">All Grades</option>
                <option value="A+">A+</option>
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="C">C</option>
                <option value="D">D</option>
              </select>

              <input
                type="range"
                min="0"
                max="100"
                value={filters.minScore}
                onChange={(e) => setFilters(prev => ({ ...prev, minScore: parseInt(e.target.value) }))}
                className="slider"
              />
              <span className="text-sm text-gray-600">Min Score: {filters.minScore}</span>

              <button
                onClick={exportResults}
                className="bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700 flex items-center"
              >
                <ArrowDownTrayIcon className="w-4 h-4 mr-1" />
                Export CSV
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Results Section */}
      {loading ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Processing leads...</p>
        </div>
      ) : filteredLeads.length > 0 ? (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold flex items-center">
              <ChartBarIcon className="w-6 h-6 text-blue-500 mr-2" />
              Scoring Results ({filteredLeads.length} leads)
            </h2>
          </div>
          
          {viewMode === 'table' ? (
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lead</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Key Factors</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredLeads.map((scoredLead) => {
                    const lead = leads.find(l => l.id === scoredLead.lead_id);
                    return (
                      <tr key={scoredLead.lead_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{lead?.name || 'Unknown'}</div>
                            <div className="text-sm text-gray-500">{lead?.email}</div>
                            <div className="text-xs text-gray-400">{lead?.source}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <span className={`text-2xl font-bold ${getScoreColor(scoredLead.score)}`}>
                              {scoredLead.score}
                            </span>
                            <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${scoredLead.score >= 80 ? 'bg-green-500' : scoredLead.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                style={{ width: `${scoredLead.score}%` }}
                              ></div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getGradeBadgeColor(scoredLead.grade)}`}>
                            {scoredLead.grade}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <span className="text-sm text-gray-900">{Math.round(scoredLead.confidence * 100)}%</span>
                            <div className="ml-2 w-12 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-500 h-2 rounded-full"
                                style={{ width: `${scoredLead.confidence * 100}%` }}
                              ></div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 max-w-xs">
                          <div className="space-y-1">
                            {scoredLead.factors.slice(0, 3).map((factor, idx) => (
                              <div key={idx} className="flex items-center text-xs">
                                <div className="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                                {factor}
                              </div>
                            ))}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-6">
              <div className="text-center text-gray-500 py-8">
                Analytics view coming soon - detailed charts and insights
              </div>
            </div>
          )}
        </div>
      ) : !loading && scoredLeads.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No scored leads yet</h3>
          <p className="text-gray-600">Upload a CSV file to start scoring your leads with AI</p>
        </div>
      ) : null}
    </div>
  );
};

export default AILeadScoring;
