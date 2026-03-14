import React from 'react';
import TopSummary from './TopSummary';
import RankedStockOutput from './RankedStockOutput';
import CompanyDeepDive from './CompanyDeepDive';

function ResultsPage({ sector, analysisResult, selectedCompany, onCompanySelect, onBackToSelection }) {
  const heroMetrics = {
    topOpportunity: analysisResult.ranked?.[0]?.company_name || 'N/A',
    bestCagr: analysisResult.ranked?.[0]?.base_cagr_pct || 0,
    stocksAnalyzed: analysisResult.company_results?.length || 0,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AnalystOS</h1>
              <p className="text-sm text-gray-500 mt-1">
                {sector.replace('_', ' ').toUpperCase()} Analysis Complete
              </p>
            </div>
            <button
              onClick={onBackToSelection}
              className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
            >
              ← New Analysis
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Top Summary */}
        <TopSummary metrics={heroMetrics} sector={sector} />

        {/* Ranked Stock Output */}
        <RankedStockOutput
          ranked={analysisResult.ranked}
          companyResults={analysisResult.company_results}
          onCompanySelect={onCompanySelect}
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
      </div>
    </div>
  );
}

export default ResultsPage;
