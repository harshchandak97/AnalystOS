import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Components
import HeroSection from './components/HeroSection';
import AnalysisPipeline from './components/AnalysisPipeline';
import SectorRanking from './components/SectorRanking';
import CompanyDeepDive from './components/CompanyDeepDive';
import SectorSelector from './components/SectorSelector';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [sectors, setSectors] = useState([]);
  const [selectedSector, setSelectedSector] = useState('power_equipment');
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(null);

  // Fetch sectors on mount
  useEffect(() => {
    fetchSectors();
  }, []);

  const fetchSectors = async () => {
    try {
      console.log('Fetching sectors from:', `${API_BASE}/api/sectors`);
      const response = await axios.get(`${API_BASE}/api/sectors`);
      console.log('Sectors response:', response.data);
      setSectors(response.data.sectors || []);
    } catch (error) {
      console.error('Error fetching sectors:', error);
      // Fallback to default sectors if API fails
      setSectors(['power_equipment', 'Technology', 'Healthcare', 'Consumer']);
    }
  };

  const runAnalysis = async () => {
    setLoading(true);
    setAnalysisResult(null);
    setSelectedCompany(null);
    
    try {
      const response = await axios.post(`${API_BASE}/api/analysis/run`, {
        sector: selectedSector,
        run_extraction: false,
      });
      setAnalysisResult(response.data);
      
      // Auto-select first company
      if (response.data.company_results && response.data.company_results.length > 0) {
        setSelectedCompany(response.data.company_results[0]);
      }
    } catch (error) {
      console.error('Error running analysis:', error);
      alert('Analysis failed. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const handleCompanySelect = (companyId) => {
    const company = analysisResult?.company_results?.find(
      c => c.company_id === companyId
    );
    if (company) {
      setSelectedCompany(company);
    }
  };

  // Calculate hero metrics
  const heroMetrics = analysisResult ? {
    topOpportunity: analysisResult.ranked?.[0]?.company_name || 'N/A',
    companiesAnalyzed: analysisResult.company_results?.length || 0,
    bestCagr: analysisResult.ranked?.[0]?.base_cagr_pct || 0,
  } : null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AnalystOS</h1>
                <p className="text-xs text-gray-500">AI-native sector analyst workflow</p>
              </div>
            </div>
            
            <SectorSelector
              sectors={sectors}
              selectedSector={selectedSector}
              onSectorChange={setSelectedSector}
              onRunAnalysis={runAnalysis}
              loading={loading}
            />
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        {heroMetrics && (
          <HeroSection metrics={heroMetrics} />
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600 font-medium">Running analysis...</p>
            </div>
          </div>
        )}

        {/* Analysis Pipeline */}
        {analysisResult && !loading && (
          <>
            <AnalysisPipeline
              stepStatuses={analysisResult.step_statuses}
              activityLog={analysisResult.activity_log}
            />

            {/* Sector Ranking */}
            <SectorRanking
              ranked={analysisResult.ranked}
              companyResults={analysisResult.company_results}
              onCompanySelect={handleCompanySelect}
              selectedCompanyId={selectedCompany?.company_id}
            />

            {/* Company Deep Dive */}
            {selectedCompany && (
              <CompanyDeepDive
                company={selectedCompany}
                rank={analysisResult.ranked?.findIndex(r => r.company_id === selectedCompany.company_id) + 1}
                total={analysisResult.ranked?.length || 0}
              />
            )}
          </>
        )}

        {/* Empty State */}
        {!loading && !analysisResult && (
          <div className="text-center py-20">
            <div className="mx-auto h-24 w-24 text-gray-400">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="mt-4 text-lg font-medium text-gray-900">No analysis yet</h3>
            <p className="mt-2 text-sm text-gray-500">
              Select a sector and click "Run Analysis" to begin
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
