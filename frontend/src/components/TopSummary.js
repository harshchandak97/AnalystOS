import React from 'react';

function TopSummary({ metrics, sector }) {
  return (
    <div className="mb-8">
      {/* Hero Cards */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl shadow-xl p-8 text-white mb-6">
        <h2 className="text-3xl font-bold mb-2">Analysis Complete</h2>
        <p className="text-blue-100 text-sm mb-6">
          AnalystOS identified the strongest risk/reward opportunity in the selected {sector.replace('_', ' ')} names 
          based on management-backed guidance and deterministic scenario modeling.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="text-blue-100 text-xs font-semibold uppercase tracking-wide mb-2">
              Top Opportunity
            </div>
            <div className="text-2xl font-bold">{metrics.topOpportunity}</div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="text-blue-100 text-xs font-semibold uppercase tracking-wide mb-2">
              Highest Base CAGR
            </div>
            <div className="text-2xl font-bold">{metrics.bestCagr.toFixed(1)}%</div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="text-blue-100 text-xs font-semibold uppercase tracking-wide mb-2">
              Stocks Analyzed
            </div>
            <div className="text-2xl font-bold">{metrics.stocksAnalyzed}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TopSummary;
