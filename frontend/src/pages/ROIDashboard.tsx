import React, { useState, useEffect } from 'react';
import axios from 'axios';

export {}; // Make this a module

interface ROIMetrics {
  leads_uploaded: number;
  calls_made: number;
  emails_sent: number;
  appointments_booked: number;
  deals_closed: number;
  revenue_generated: number;
  cost_per_lead: number;
  conversion_rate: number;
  roi_percentage: number;
  projected_monthly_revenue: number;
}

interface Recommendation {
  category: string;
  title: string;
  description: string;
  impact: string;
  effort: string;
}

interface CompetitivePosition {
  roi_percentile: number;
  conversion_percentile: number;
  overall_grade: string;
  beat_competitors: boolean;
  improvement_areas: string[];
}

interface ROIData {
  metrics: ROIMetrics;
  insights: string[];
  recommendations: Recommendation[];
  competitive_position: CompetitivePosition | null;
  timeframe_days: number;
}

const ROIDashboard: React.FC = () => {
  const [roiData, setRoiData] = useState<ROIData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [timeframe, setTimeframe] = useState('30');
  const [industry, setIndustry] = useState('medspas');
  const [dateRange, setDateRange] = useState('');

  useEffect(() => {
    loadROIData();
  }, [timeframe, industry]);

  const loadROIData = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get('/api/analytics/roi', {
        params: {
          days: timeframe,
          industry: industry,
          date_range: dateRange || undefined
        }
      });
      setRoiData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load ROI data');
    } finally {
      setLoading(false);
    }
  };

  const exportReport = async () => {
    try {
      const response = await axios.get('/api/analytics/roi/export', {
        params: {
          days: timeframe,
          industry: industry,
          format: 'pdf'
        },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `roi_report_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setSuccess('Report exported successfully!');
    } catch (err) {
      setError('Failed to export report');
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const getROIColor = (roi: number) => {
    if (roi >= 300) return 'text-green-600';
    if (roi >= 200) return 'text-blue-600';
    if (roi >= 100) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getEffortColor = (effort: string) => {
    switch (effort.toLowerCase()) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <span className="w-8 h-8 text-blue-500 mr-3">📊</span>
          ROI Dashboard
        </h1>
        <p className="text-gray-600 mt-2">
          Track your return on investment and identify growth opportunities
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Time Period</label>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="365">Last year</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Industry</label>
            <select
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="medspas">Med Spas</option>
              <option value="contractors">Contractors</option>
              <option value="law_firms">Law Firms</option>
              <option value="real_estate">Real Estate</option>
              <option value="healthcare">Healthcare</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Custom Date Range</label>
            <input
              type="date"
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            />
          </div>

          <div className="flex items-end gap-2">
            <button
              onClick={loadROIData}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 disabled:bg-gray-400"
            >
              {loading ? 'Loading...' : 'Refresh'}
            </button>
            
            <button
              onClick={exportReport}
              className="bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700 flex items-center"
            >
              📥 Export
            </button>
          </div>
        </div>
      </div>

      {/* Success/Error Messages */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 flex items-center">
          ⚠️ {error}
        </div>
      )}

      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6 flex items-center">
          ✅ {success}
        </div>
      )}

      {loading ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading ROI data...</p>
        </div>
      ) : roiData ? (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <span className="w-6 h-6 text-green-600">💰</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Revenue Generated</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {formatCurrency(roiData.metrics.revenue_generated)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <span className="w-6 h-6 text-blue-600">📈</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">ROI Percentage</p>
                  <p className={`text-2xl font-semibold ${getROIColor(roiData.metrics.roi_percentage)}`}>
                    {formatPercentage(roiData.metrics.roi_percentage)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <span className="w-6 h-6 text-purple-600">👥</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Conversion Rate</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {formatPercentage(roiData.metrics.conversion_rate)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <span className="w-6 h-6 text-orange-600">📊</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Cost Per Lead</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {formatCurrency(roiData.metrics.cost_per_lead)}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Activity Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-md p-4 text-center">
              <div className="flex justify-center mb-2">
                <span className="text-4xl">👥</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{roiData.metrics.leads_uploaded}</p>
              <p className="text-sm text-gray-500">Leads Uploaded</p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-4 text-center">
              <div className="flex justify-center mb-2">
                <span className="text-4xl">📞</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{roiData.metrics.calls_made}</p>
              <p className="text-sm text-gray-500">Calls Made</p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-4 text-center">
              <div className="flex justify-center mb-2">
                <span className="text-4xl">✉️</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{roiData.metrics.emails_sent}</p>
              <p className="text-sm text-gray-500">Emails Sent</p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-4 text-center">
              <div className="flex justify-center mb-2">
                <span className="text-4xl">📅</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{roiData.metrics.appointments_booked}</p>
              <p className="text-sm text-gray-500">Appointments</p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-4 text-center">
              <div className="flex justify-center mb-2">
                <span className="text-4xl">✅</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{roiData.metrics.deals_closed}</p>
              <p className="text-sm text-gray-500">Deals Closed</p>
            </div>
          </div>

          {/* Competitive Position & Insights */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Competitive Position */}
            {roiData.competitive_position && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center">
                  <span className="w-6 h-6 text-blue-500 mr-2">🏆</span>
                  Competitive Position
                </h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">Overall Grade</p>
                      <p className="text-sm text-gray-500">
                        {roiData.competitive_position.beat_competitors 
                          ? 'Outperforming competitors' 
                          : 'Room for improvement'}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        roiData.competitive_position.overall_grade === 'A' ? 'bg-green-100 text-green-800' :
                        roiData.competitive_position.overall_grade === 'B' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        Grade {roiData.competitive_position.overall_grade}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-gray-700">ROI Percentile</p>
                      <div className="flex items-center mt-1">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${roiData.competitive_position.roi_percentile}%` }}
                          ></div>
                        </div>
                        <span className="ml-2 text-sm text-gray-600">
                          {Math.round(roiData.competitive_position.roi_percentile)}%
                        </span>
                      </div>
                    </div>

                    <div>
                      <p className="text-sm font-medium text-gray-700">Conversion Percentile</p>
                      <div className="flex items-center mt-1">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${roiData.competitive_position.conversion_percentile}%` }}
                          ></div>
                        </div>
                        <span className="ml-2 text-sm text-gray-600">
                          {Math.round(roiData.competitive_position.conversion_percentile)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {roiData.competitive_position.improvement_areas.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Areas for Improvement</p>
                      <ul className="space-y-1">
                        {roiData.competitive_position.improvement_areas.map((area, idx) => (
                          <li key={idx} className="text-sm text-gray-600 flex items-center">
                            <div className="w-2 h-2 bg-orange-400 rounded-full mr-2"></div>
                            {area}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Insights */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <span className="w-6 h-6 text-green-500 mr-2">💡</span>
                Key Insights
              </h2>
              
              <div className="space-y-3">
                {roiData.insights.map((insight, idx) => (
                  <div key={idx} className="flex items-start p-3 bg-blue-50 rounded-lg">
                    <span className="w-5 h-5 text-blue-500 mr-2 mt-0.5 flex-shrink-0">✅</span>
                    <p className="text-sm text-gray-700">{insight}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Growth Recommendations */}
          {roiData.recommendations.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <span className="w-6 h-6 text-purple-500 mr-2">🚀</span>
                Growth Recommendations
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {roiData.recommendations.map((rec, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-medium text-gray-900">{rec.title}</h3>
                      <div className="flex gap-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(rec.impact)}`}>
                          {rec.impact} Impact
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getEffortColor(rec.effort)}`}>
                          {rec.effort} Effort
                        </span>
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">{rec.description}</p>
                    
                    <div className="text-xs text-gray-500 bg-gray-50 rounded px-2 py-1">
                      Category: {rec.category}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Projection */}
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
            <h2 className="text-xl font-semibold mb-2">Monthly Revenue Projection</h2>
            <p className="text-3xl font-bold">
              {formatCurrency(roiData.metrics.projected_monthly_revenue)}
            </p>
            <p className="text-blue-100 mt-1">
              Based on current performance trends over {roiData.timeframe_days} days
            </p>
          </div>
        </>
      ) : !loading ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <span className="text-6xl mb-4 block">📊</span>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No ROI data available</h3>
          <p className="text-gray-600">Start by uploading leads and making calls to see your ROI metrics</p>
        </div>
      ) : null}
    </div>
  );
};

export default ROIDashboard;
